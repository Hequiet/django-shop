from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from requestdataapp.forms import USerBioForm, UploadFileForm


def process_get_view(request: HttpRequest) -> HttpResponse:
    context = {

    }
    return render(request, "requestdataapp/request-query-params.html", context)

def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": USerBioForm()
    }
    return render(request,"requestdataapp/user-bio-form.html", context=context)

def handle_file_upload(request: HttpRequest) -> HttpResponse:

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data['file']
            if myfile.size > 1024:
                return render(request, 'requestdataapp/file-upload.html',
                              {"error": f"Файл слишком большой! Максимум 1024 Б"})
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print("saved file", filename)
    else:
        form = UploadFileForm()
    context = {
        "form": form
    }
    return render(request,"requestdataapp/file-upload.html", context=context)
