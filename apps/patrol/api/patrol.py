import base64
import os

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods

from apps.permission_manager.util.api_permission import api_permission
from apps.user_manager.util.userUtils import get_user_by_id
from util.Request import RequestLoadJson
from util.Response import ResponseJson
from util.asgi_file import get_file_response
from util.logger import Log
from apps.patrol.models import Patrol, UploadedImage
from util.pageUtils import get_page_content, get_max_page

img_save_path = os.path.join(os.getcwd(),"uploads")


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
        image_id = data.get("image_id")  # 假设前端传递了图片ID
        if content is None or status is None or title is None:
            return ResponseJson({"status": -1, "msg": "参数错误"}, 400)
        Patrol.objects.create(user_id=user_id, content=content, status=status, title=title, img_id=image_id)
    return ResponseJson({"status": 1, "msg": "添加成功"})


@require_POST
@api_permission("viewPatrol")
def upload_image(request):
    if request.method == 'POST':
        if 'image' in request.FILES:
            image = request.FILES['image']
            uploaded_image = UploadedImage.objects.create(image=image)
            return JsonResponse({"message": "Image uploaded successfully!", "image_id": uploaded_image.id})
        return JsonResponse({"error": "No image provided"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)


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
        result = Patrol.objects.filter()
        pageQuery = get_page_content(result, page if page > 0 else 1, pageSize)
        if pageQuery:
            for item in pageQuery:
                img=UploadedImage.objects.get(id=item.get("img_id"))
                image_path = os.path.join(os.getcwd(), str(img.image))
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                    img64 = base64.b64encode(img_data).decode('utf-8')
                PageContent.append({
                    "id": item.get("id"),
                    "user": get_user_by_id(item.get("user_id")).userName if item.get("user_id") else None,
                    "content": item.get("content"),
                    "status": item.get("status"),
                    "title": item.get("title"),
                    "time": item.get("time"),
                    "imgId": img64
                })

        return ResponseJson({
            "status": 1,
            "data": {
                "maxPage": get_max_page(result.count(), 20),
                "currentPage": page,
                "PageContent": PageContent
            }
        })




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
    Patrol.objects.filter(id=id).delete()
    return ResponseJson({"status": 1, "msg": "删除成功"})
