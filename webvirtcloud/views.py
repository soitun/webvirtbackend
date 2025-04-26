from http import HTTPStatus

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def success_message_response(message):
    status_code = status.HTTP_200_OK
    success_payload = {
        "message": message,
        "status_code": status_code,
    }
    return Response(success_payload, status=status_code)


def error_message_response(message):
    status_code = status.HTTP_400_BAD_REQUEST
    error_payload = {
        "message": message,
        "status_code": status_code,
    }
    return Response(error_payload, status=status_code)


def app_exception_handler(exc, context):
    error_message = None
    response = exception_handler(exc, context)

    if response is not None:
        error_fileds = []
        error_payload = {
            "message": "",
            "status_code": 0,
        }
        status_code = response.status_code

        if isinstance(response.data, dict):
            detail_error = response.data.get("detail")
            non_field_error = response.data.get("non_field_errors")

            if detail_error:
                error_message = detail_error
                if status_code == HTTPStatus.NOT_FOUND:
                    error_message = "The resource you were accessing could not be found."
                if status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                    error_message = "The resource you were accessing got internal error."

            if non_field_error:
                error_message = non_field_error[0]

        if isinstance(response.data, list):
            error_message = response.data[0]

        if not error_message:
            for key, value in response.data.items():
                if isinstance(value, list):
                    error_fileds.append({key: value[0]})
                if isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, list):
                            error_fileds.append({k: v[0]})
                        else:
                            error_fileds.append({k: v})
            error_payload["errors"] = error_fileds
            error_message = HTTPStatus(status_code).description

        error_payload["message"] = error_message
        error_payload["status_code"] = status_code
        response.data = error_payload
    return response


def app_exception_handler403(request, exception):
    status_code = 403

    if "api/" in request.META["PATH_INFO"]:
        response = JsonResponse(
            {
                "status_code": status_code,
                "message": "Forbidden",
            },
            content_type="application/json",
            status=status_code,
        )
        return response

    return render(request, "403.html", status=status_code)


def app_exception_handler404(request, exception):
    status_code = 404

    if "api/" in request.META["PATH_INFO"]:
        response = JsonResponse(
            {
                "status_code": status_code,
                "message": "The resource you were accessing could not be found.",
            },
            content_type="application/json",
            status=status_code,
        )
        return response

    return render(request, "404.html", status=status_code)


def app_exception_handler500(request):
    status_code = 500

    if "api/" in request.META["PATH_INFO"]:
        response = JsonResponse(
            {
                "status_code": status_code,
                "message": "The resource you were accessing got internal error.",
            },
            content_type="application/json",
            status=status_code,
        )
        return response

    return render(request, "500.html", status=status_code)


class IndexView(TemplateView):
    template_name = "client/index.html"

    @method_decorator(ensure_csrf_cookie, name="dispatch")
    def dispatch(self, request, *args, **kwargs):
        if request.user and request.user.is_superuser:
            return redirect(reverse_lazy("admin_index"))
        return super(IndexView, self).dispatch(request, *args, **kwargs)
