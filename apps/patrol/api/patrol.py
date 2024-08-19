import base64
import os

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods

from apps.audit.util.auditTools import write_audit, write_file_change_log
from apps.permission_manager.util.api_permission import api_permission
from apps.user_manager.util.userUtils import get_user_by_id
from util import result, file_util, uploadFile
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.asgi_file import get_file_response
from util.logger import Log
from apps.patrol.models import Patrol
from util.pageUtils import get_page_content, get_max_page
from util.uploadFile import upload_chunk

FILE_SAVE_BASE_PATH = os.path.join(os.getcwd(), "data", "patrol")



@require_POST
@api_permission("viewPatrol")
def addARecord(req: HttpRequest):
    try:
        data = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    else:
        user_id = req.session.get("userID")
        content = data.get("content")
        status = data.get("status")
        title = data.get("title")
        image_list = data.get("images")
        if content is None or status is None or title is None:
            return ResponseJson({"status": -1, "msg": "参数错误"}, 400)
        data = Patrol.objects.create(user_id=user_id, content=content, status=status, title=title)
        for image in image_list:
            if not os.path.exists(os.path.join(FILE_SAVE_BASE_PATH, image)):
                continue
            if Patrol.Image.objects.filter(image_hash=image).exists():
                image_obj = Patrol.Image.objects.filter(image_hash=image).first()
            else:
                image_obj = Patrol.Image.objects.create(image_hash=image)
            data.image_list.add(image_obj)
        if len(image_list) > 0:
            data.save()
    return result.success()


@require_POST
@api_permission("viewPatrol")
def upload_image_chunk(request: HttpRequest):
    """
    上传图片文件块
    """
    return uploadFile.upload_chunk(request)

@require_POST
@api_permission("viewPatrol")
def merge_image(request: HttpRequest):
    """
    合并图片文件块并返回文件哈希
    """
    user = get_user_by_id(request.session["userID"])
    file_name = request.POST.get("file_name")
    if not os.path.exists(FILE_SAVE_BASE_PATH):
        os.makedirs(FILE_SAVE_BASE_PATH)
    merge_status, hash256 = uploadFile.merge_chunks(request, FILE_SAVE_BASE_PATH, True)
    if merge_status:
        write_audit(user, "上传图片", "巡检记录", f"{file_name} (hash256: {hash256})")
        return JsonResponse({'status': 1, 'data': {
            'file_name': file_name,
            'hash': hash256,
        }})
    return JsonResponse({'status': 0})

@require_POST
@api_permission("viewPatrol")
def getList(req: HttpRequest):
    try:
        data = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    else:
        PageContent = []
        page = data.get("page", 1)
        pageSize = data.get("pageSize", 20)
        result = Patrol.objects.all()
        pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
        if pageQuery:
            for item in pageQuery:
                patrol = Patrol.objects.get(id=item.get('id'))
                Log.debug(patrol.image_list.all())
                PageContent.append({
                    "id": item.get("id"),
                    "user": get_user_by_id(item.get("user_id")).userName if item.get("user_id") else None,
                    "content": item.get("content"),
                    "status": item.get("status"),
                    "title": item.get("title"),
                    "time": item.get("time"),
                    "images": [img.image_hash for img in patrol.image_list.all()],
                })

        return ResponseJson({
            "status": 1,
            "data": {
                "maxPage": get_max_page(result.count(), 20),
                "currentPage": page,
                "PageContent": PageContent
            }
        })


@require_http_methods("GET")
@api_permission("viewPatrol")
def get_image(req: HttpRequest, image):
    """
    获取图片
    """
    if not os.path.exists(os.path.join(FILE_SAVE_BASE_PATH, image)):
        return get_file_response('public/no-image.png')
    return get_file_response(os.path.join(FILE_SAVE_BASE_PATH, image))


@require_http_methods("PUT")
@api_permission("editPatrol")
def updateRecord(req: HttpRequest):
    try:
        data = RequestLoadJson(req)
    except Exception as e:
        Log.error(e)
        return ResponseJson({"status": -1, "msg": f"JSON解析失败:{e}"}, 400)
    else:
        id = data.get("id")
        content = data.get("content")
        status = data.get("status")
        title = data.get("title")
        if id is None or content is None or status is None or title is None:
            return ResponseJson({"status": -1, "msg": "参数错误"}, 400)
        Patrol.objects.filter(id=id).update(content=content, status=status, title=title)
    return ResponseJson({"status": 1, "msg": "更新成功"})


@require_http_methods("DELETE")
@api_permission("editPatrol")
def deleteRecord(req: HttpRequest):
    id = req.GET.get("id")
    if id is None:
        return ResponseJson({"status": -1, "msg": "参数错误"}, 400)
    if not Patrol.objects.filter(id=id).exists():
        return ResponseJson({"status": -1, "msg": "记录不存在"}, 400)
    if not req.session.get("userID") == Patrol.objects.get(id=id).user_id:
        return ResponseJson({"status": -1, "msg": "权限不足"})
    patrol:Patrol = Patrol.objects.filter(id=id).first()
    if patrol:
        for image in patrol.image_list.all():
            if not Patrol.objects.filter(image_list=image).exists(id=patrol.id).exists():
                Log.debug(f"删除图片记录{image.image_hash}")
                try:
                    os.remove(os.path.join(FILE_SAVE_BASE_PATH, image.image_hash))
                except Exception:
                    pass
                image.delete()
    patrol.delete()
    return ResponseJson({"status": 1, "msg": "删除成功"})
