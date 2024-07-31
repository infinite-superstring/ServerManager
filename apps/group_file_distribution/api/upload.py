from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

from util import uploadFile


@require_POST
def upload_file_chunk(req: HttpRequest) -> HttpResponse:
    return uploadFile.upload_chunk(req)


@require_POST
def merge_file(req: HttpRequest) -> HttpResponse:
    return uploadFile.merge_chunks(req)
