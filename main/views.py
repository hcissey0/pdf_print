from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpRequest, FileResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from wsgiref.util import FileWrapper

from django.conf import settings
import os
from .models import PdfFile

# Create your views here.

def index(request: HttpRequest):
    print("Request: ", request)
    print("Cookies: ", request.COOKIES)
    print("Headers: ", request.headers)
    print("Host: ", request.get_host())
    print(settings.BASE_DIR)
    return render(request, 'index.html')


def register_view(request: HttpRequest):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('main:register')
        
        if User.objects.filter(username=username):
            messages.error(request, 'Username already taken')
            return redirect('main:register')
        
        if User.objects.filter(email=email):
            messages.error(request, 'Email already in use')
            return redirect('main:register')
        
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        user.save()
        messages.success(request, 'Account created successfully')
        return redirect('main:login')
    return render(request, 'register.html')


def login_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)
        if not user:
            messages.error(request, 'Invalid username')
            return redirect('main:login')
        user = User.objects.get(username=username)
        if not user.password == password:
            messages.error(request, 'Wrong password')
            return redirect('main:login')

        login(request, user)
        messages.success(request, 'Login successful')
        return redirect('main:index')

    return render(request, 'login.html')


def logout_view(request: HttpRequest):
    logout(request)
    return redirect('main:index')


def about(request: HttpRequest):
    return render(request, 'about.html')

@login_required
def upload_file(request: HttpRequest):
    if request.method == 'POST':
        print("Post: ", request.POST)
        print("Files: ", request.FILES)
        
        file = request.FILES.get('file')
        if not file or not file.name:
            return JsonResponse({'error': 'No File Uploaded'}, status=404)

        if not file.name.endswith('.pdf'):
            return JsonResponse({'error': 'Only pdf files allowed'}, status=404)
        new_file = PdfFile(user=request.user, name=file.name, file=file)
        new_file.save()

        return JsonResponse({'success': 'File Uploaded successfully'}, status=201)
    return JsonResponse({'error': 'Not a POST method'}, status=404)



def test_upload(request):
    return render(request, 'test.html')

@login_required
def get_files_list(request: HttpRequest):
    print('get file list called')
    return render(request, 'files_list.htm')

@require_POST
@login_required
def delete_file(request: HttpRequest, file_id):
    print("Delete called")
  
    if not PdfFile.objects.filter(id=file_id):
        return JsonResponse({"error": "not found"})
    file = PdfFile.objects.get(pk=file_id)
    if not file:
        return JsonResponse({'error': 'File not found.'})
    file.delete()
    return JsonResponse({'success': "File deleted."})
   
@login_required
def simplex(request: HttpRequest):
    if request.method == 'POST':
        print("Post: ", request.POST)
        print("Files: ", request.FILES)

        if request.FILES:
            try:
                if request.user.file:
                    return JsonResponse({'success': "You can only upload one file at a time"})
            except:
                pass
            file = request.FILES.get('file')
            if not file:
                return JsonResponse({'error': 'No file present'}, status=404)
            pdffile = PdfFile(user=request.user, file=file, name=file.name)
            pdffile.save()
            return JsonResponse({'success': 'File uploaded successfully.'})
        elif request.POST:
            print(request.user.file)
            pdf_file = request.user.file
            page_mode = request.POST.get('page_mode')
            book_form = request.POST.get('book_form')
            bind_mode = request.POST.get('bind_mode')

            # print("media: ", settings.MEDIA_URL)
            file_url = str(settings.BASE_DIR) + str(pdf_file.file.url)
            # print(pdf_file.file.name)
            # file_url = '/'.join(file_url.split('/')[:-1]) + '/' + pdf_file.name
            # print(file_url.split('/')[:-1])
            # print('/'.join(file_url.split('/')[:-1]))
            print(file_url)
            
            pages = handle_simplex_file(file_url, page_mode, book_form, bind_mode)

            if not pages:
                return JsonResponse({'error': 'Error occured'})
            
            
            return JsonResponse({
                'success': {
                    'frontpages': pages.get('frontpages').split('/')[-1],
                    'backpages': pages.get('backpages').split('/')[-1]
                }
            })
        else:
            return JsonResponse({'error': "There's an error somewhere"})
            

    return render(request, 'simplex.html')

@login_required
def get_filename_id(request: HttpRequest):

    try:
        file = request.user.file
    except:
        return JsonResponse({'error': 'User has no files'}, status=404)
    context = {'filename': file.name, 'file_id': file.id}
    print(context)
    return JsonResponse(context)


@login_required
def download(request: HttpRequest, filename: str):
    file_url = request.user.file.file.url
    url = str(settings.BASE_DIR) + str(file_url)
    path = url[:-4] + '/'
    print("path from download: ", path)
    if not os.path.exists(path):
        return JsonResponse({'error': 'Not found'})
    print("url: ", url)
    print('path: ', path)

    file_path = path + filename
    print('file path from dowload: ', file_path)
    if not os.path.exists(file_path):
        return JsonResponse({'error': 'Not found'})
    
    file_wrapper = FileWrapper(open(file_path, 'rb'))
    response = FileResponse(
        file_wrapper,
        content_type='application/pdf'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response
    


def handle_simplex_file(file_url: str, page_mode: str, book_form: str, bind_mode: str) -> dict:
    """This handles the simplex mode.
    It takes the files and then split it into front and back pages.

    Args:
        file_url (str): This is the file url (absolute)
        page_mode (str): The is the page mode (1, 2 or 4)
        book_form (str): The form the book would take after print
        bind_mode (str): The bind mode of the book (either left or right)

    Returns:
        dict: The two files' urls, the frontpages pdf and the backpages pdf.
    """
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(file_url)
    print(len(reader.pages))
    print(file_url)
    # Gets the url except the file name
    url = file_url[::-1][file_url[::-1].index('/'):][::-1]
    # Gets the file name
    filename = file_url.split('/')[-1]
    print(filename)
    print(url)
    
    writer = PdfWriter()
    
    frontpages = PdfWriter()
    backpages = PdfWriter()

    temp_writer = PdfWriter()
    for page in reader.pages: # Copy all the pdf pages to the main writer
        writer.add_page(page)
    tok = 1 if len(writer.pages) > 1 else 0 # The page dimensions to use (usually second)

    # 1 page mode
    if page_mode == '1':
        while len(writer.pages) % 2 != 0:   # Making sure the number of pages is divisible by 2
            writer.add_blank_page(          # otherwise append blank pages to the pdf
                width=writer.pages[tok].mediabox.width,
                height=writer.pages[tok].mediabox.height
            )

        for i in range(len(writer.pages)):
            if i % 2 == 0: # if index is even then it's a front page otherwise back page
                frontpages.insert_page(writer.pages[i], index=i+1)
            else:
                backpages.insert_page(writer.pages[i], index=i+1)

        
        # Take note that the left and right bind mode doesn't have effect on the 1 page mode
        # since the bind mode will depend on the the type and how the user will
        # stitch the final product after print.
        # And the book_form also won't have effect since it is a single page

    # 2 page mode
    elif page_mode == '2':
        while len(writer.pages) % 4 != 0:
            writer.add_blank_page(
                width=writer.pages[tok].mediabox.width,
                height=writer.pages[tok].mediabox.height
            )
        
        for i in range(len(writer.pages)//2):
            temp_writer.add_blank_page(
                width=writer.pages[tok].mediabox.width*2,
                height=writer.pages[tok].mediabox.height
            )
        
        if book_form == 'booklet':
            if bind_mode == 'left':
                for i in range(len(writer.pages)//2):
                    if i % 2 == 0:
                        temp_writer.pages[i].merge_translated_page(
                            writer.pages[i],
                            tx=writer.pages[tok].mediabox.width,
                            ty=0.0
                        )
                        temp_writer.pages[i].merge_translated_page(
                            writer.pages[-(i+1)],
                            tx=0.0,
                            ty=0.0
                        )
                    else:
                        temp_writer.pages[i].merge_translated_page(
                            writer.pages[-(i+1)],
                            tx=writer.pages[tok].mediabox.width,
                            ty=0.0
                        )
                        temp_writer.pages[i].merge_translated_page(
                            writer.pages[i],
                            tx=0.0,
                            ty=0.0
                        )
                print('2 left')
            elif bind_mode == 'right':
                for i in range(len(writer.pages)//2):
                    if i % 2 == 0:
                        temp_writer.pages[i].merge_translated_page(
                            writer.pages[i],
                            tx=0.0,
                            ty=0.0
                        )
                        temp_writer.pages[i].merge_translated_page(
                            writer.pages[-(i+1)],
                            tx=writer.pages[tok].mediabox.width,
                            ty=0.0
                        )
                    else:
                        temp_writer.pages[i].merge_translated_page(
                            writer.pages[-(i+1)],
                            tx=0.0,
                            ty=0.0
                        )
                        temp_writer.pages[i].merge_translated_page(
                            writer.pages[i],
                            tx=writer.pages[tok].mediabox.width,
                            ty=0.0
                        )
                print('2 right')
            else:
                return None
        elif book_form == 'continuous':
            pass
        else:
            return None
    elif page_mode == '4':
        if bind_mode == 'left':
            print('4 left')
        elif bind_mode == 'right':
            print('4 right')
        else:
            return None
    else:
        return None

    path = url + filename[:-4] + '/'
    if not os.path.exists(path):
        os.makedirs(path)

    # urls for the pages
    frontpages_url = path + "frontpages-" + filename
    backpages_url = path + 'backpages-' + filename

    for i in range(len(temp_writer.pages)):
        if i % 2 == 0:
            frontpages.add_page(temp_writer.pages[i])
        else:
            backpages.add_page(temp_writer.pages[-i])
    
    with open(frontpages_url, 'wb') as f:
        frontpages.write(f) # save front pages

    with open(backpages_url, 'wb') as f:
        backpages.write(f) # save back pages

    writer.close()
    temp_writer.close()
    frontpages.close()
    backpages.close()

    return {'frontpages': frontpages_url, 'backpages': backpages_url}


def handle_duplex_file(file, page_mode, bind_mode):
    pass


