from django.shortcuts import redirect, render
from .models import Blog, BlogComment, ForgottenPassword, ProfilePhoto, PaidPromotion
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import check_password
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

def otpGen():
    import random
    otp = ""
    for OTP in range(4):
        otp += str(random.randint(1, 9))
    return otp
user_otp = otpGen()

def sendEmail(receiver_name, receiver_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header('Anirban Bhattacharya')), "no-reply@anirbanbhattacharya.in"))
    msg['To'] = receiver_email
    msg["Subject"] = subject
    html = message
    msg.attach(MIMEText(html, 'html'))
    s = smtplib.SMTP('smtp.gmail.com', port=587)
    s.starttls()
    s.login("contact.anirbanbhattacharya@gmail.com", "kuqgluftjyomehnx")
    s.sendmail("no-reply@anirbanbhattacharya.in", receiver_email, msg.as_string())
    s.quit()
    return None

# Articles views starts here.
def index(request):
    blogs = Blog.objects.all()
    ads = PaidPromotion.objects.all()
    ads_count = PaidPromotion.objects.count()
    ads_counts = ads_count - 1
    blog_count = Blog.objects.count()
    blog_counts = blog_count - 1
    blogparams = {
        "blogs" : blogs[Blog.objects.count() - (Blog.objects.count() - 1):Blog.objects.count():-1],
        "item1" : blogs[blog_counts - 0],
        "item2" : blogs[blog_counts - 1],
        "item3" : blogs[blog_counts - 2],
        "blog_counts" : 1,
        "adsitem1" : ads[ads_counts - 0],
        "adsitem2" : ads[ads_counts - 1],
        "adsitem3" : ads[ads_counts - 2],
    }
    return render(request, "index.html", blogparams)

def ErrorPage(request):
    return render(request, "error page.html")

def AboutUs(request):
    return render(request, "about us.html")

def Blogs(request):
    blogs = Blog.objects.all()
    return render(request, "blogs.html", {"blogs" : blogs, "recblogs" : blogs[Blog.objects.count() - (Blog.objects.count() - 1):Blog.objects.count():-1]})

def ReadBlog(request, slug):
    blogs = Blog.objects.get(BlogSlug = slug)
    intblogviews = int(blogs.Views)
    blogs.Views = intblogviews + 1
    blogs.save()
    return render(request, "read blog.html", {
        "name" : blogs.BlogName, "date" : blogs.BlogDateAdded,
        "desc" : blogs.BlogDescription,
        "image" : blogs.BlogImage,
        "cat" : blogs.BlogCategory,
        "post" : blogs.BlogPost,
        "author" : blogs.BlogAuthor,
        "views" : blogs.Views,
        "likes" : blogs.Likes.count, 
        "allblogs" : (Blog.objects.all())[Blog.objects.count() - (Blog.objects.count() - 1):Blog.objects.count():-1],
        "comments" : BlogComment.objects.filter(BlogDetails=blogs),
        "comments_count" : BlogComment.objects.filter(BlogDetails=blogs).count(),
        "blogid" : blogs.id,
        "views" : blogs.Views,
        "keywords" : blogs.BlogKeywords,
    })

def Register(request):
    return render(request, "register page.html")

def Login(request):
    return render(request, "login page.html")

def RegisterDone(request):
    if  request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        if pass1 != pass2:
            messages.warning(request, "Passwords Unmatched.")
            return redirect("Register")
        if User.objects.filter(username=email).exists():
            messages.warning(request, "A similar email address is already registered with us.")
            return redirect("Register")
        creating_user = User.objects.create_user(username=email, password=pass1, last_name=phone)
        creating_user.email = user_otp
        creating_user.first_name = name
        creating_user.save()
        authenticating = authenticate(username=email, password=pass1)
        if authenticating is not None:
            sendEmail(name, email, "Account Created", "Welcome to the Articles community! We're delighted to inform you that your account has been created. Your support means the world to us, and we're thrilled to have you on board. Kindly note that the email address you used to create your account is now permanent. Rest assured, it will be your trusted companion throughout your journey with us. Once again, thank you for choosing Articles. We look forward to sharing many wonderful experiences together.")
            login(request, authenticating)
            userdet = User.objects.get(username = request.user.username)
            creating_profile_photo = ProfilePhoto(UserDetails = userdet, Photo = "UserProfilePhoto/User profile.png")
            creating_profile_photo.save()
            messages.success(request, "Your Articles account has been created.")
        else:
            messages.warning(request, "Registration failed.")
        return redirect("HomePage")
    return redirect("ErrorPage")

def LoginDone(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        authenticating = authenticate(username=email, password=password)
        if authenticating is not None:
            login(request, authenticating)
            messages.success(request, "Logged IN")
        else:
            messages.warning(request, "Please enter details correctly.")
            return redirect("Login")
        return redirect("HomePage")
    return redirect("ErrorPage")

def Logout(request):
    logout(request)
    messages.success(request, "Logged OUT")
    return redirect("HomePage")

def UserProfile(request):
    if request.user.is_authenticated:
        userdet = User.objects.get(username = request.user.username)
        return render(request, "user profile.html", {
            "image" : ProfilePhoto.objects.get(UserDetails = userdet)
        })
    else:
        return redirect("ErrorPage")

def EditUserProfile(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        pwd = request.POST["password"]
        user_details = User.objects.get(username = email)
        if check_password(pwd, request.user.password):
            userdet = User.objects.get(username=email)
            userdet.first_name = name
            userdet.last_name = phone
            userdet.save()
            if BlogComment.objects.filter(UserDetails = user_details).exists():
                edit_comments = BlogComment.objects.get(UserDetails = user_details)
                edit_comments.Name = name
                edit_comments.save()
            if len(request.FILES) != 0:
                photo = request.FILES["photo"]
                profilephoto = ProfilePhoto.objects.get(UserDetails = user_details)
                profilephoto.Photo = photo
                profilephoto.save()
                get_photo = ProfilePhoto.objects.get(UserDetails = user_details)
                if BlogComment.objects.filter(UserDetails = user_details).exists():
                    edit_comments = BlogComment.objects.get(UserDetails = user_details)
                    edit_comments.User_ProfilePhoto = get_photo.Photo
                    edit_comments.save()
            sendEmail(name, email, "Profile Updated", "We are pleased to inform you that your Articles profile has been updated. Your commitment to enhancing your profile is truly appreciated, and we extend our heartfelt gratitude for your attention to detail. Thank you for choosing Articles as your platform for expression and connection. Your dedication enriches our community, and we look forward to continuing this journey together.")
            messages.success(request, "Your profile has been updated.")
        else:
            messages.warning(request, "Incorrect password entered.")
        return redirect("UserProfile")
    return redirect("ErrorPage") 

def DeleteAccount(request):
    if request.method == "POST":
        pwd = request.POST["password"]
        if check_password(pwd, request.user.password):
            userdet = User.objects.get(username=request.user.username)
            sendEmail(request.user.first_name, request.user.username, "Account Deleted", "It is with a heavy heart that we bid you farewell. Your departure saddens us deeply, but it also serves as a poignant reminder of the importance of continually improving our service. Your feedback is invaluable in this pursuit of excellence. We kindly request that you take a moment to share your thoughts on our website or simply reply to this email. Rest assured, every comment and suggestion will be carefully considered as we strive to enhance our offerings. Thank you for entrusting us with your experience, and we sincerely hope to have the opportunity to serve you again in the future.")
            userdet.delete()
            messages.success(request, "We are really feeling very bad to see you go.")
            return redirect("HomePage")
        else:
            messages.warning(request, "Incorrect password entered.")
            return redirect("UserProfile")
    return redirect("ErrorPage")

def VerifyEmail(request):
    if request.user.is_authenticated:
        sendEmail(request.user.first_name, request.user.username, "OTP | Articles", f"Thank you for undergoing the verification process. Your OTP is {request.user.email}.")
        return render(request, "verify email.html")
    else:
        return redirect("ErrorPage")

def EmailVerified(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        email = request.user.username
        OTP = request.user.email
        if otp == OTP:
            userdet = User.objects.get(username=email)
            userdet.email = "None"
            userdet.save()
            sendEmail(request.user.first_name, userdet.username, "Email Verified", "We extend our sincere gratitude to you for verifying your email address. Your prompt action reflects a commendable sense of responsibility, and we truly appreciate your diligence. Thank you for demonstrating your commitment to maintaining the integrity of our platform. Should you require any further assistance or have any questions, please do not hesitate to reach out to us. Once again, thank you for your cooperation and trust in our services.")
            messages.success(request, "Your email has been verified.")
            return redirect("HomePage")
        else:
            messages.warning(request, "Incorrect OTP entered.")
        return render(request, "verify email.html")
    return redirect(request, "ErrorPage") 

def ResendOTP(request):
    if request.user.is_authenticated:
        userdet = User.objects.get(username=request.user.username)
        userdet.email = user_otp
        userdet.save()
        sendEmail(request.user.first_name, request.user.username, "New OTP | Articles", f"Thank you for requesting an OTP. Your new OTP is {request.user.email}.")
        messages.success(request, "A new OTP has been sent to you.")
        return render(request, "verify email.html")
    else:
        return redirect("ErrorPage")

def ChangePassword(request):
    if request.method == "POST":
        name = request.user.first_name
        email = request.user.username
        oldpass = request.POST["oldpass"]
        newpass = request.POST["newpass"]
        confpass = request.POST["confpass"]
        if newpass != confpass:
            messages.warning(request, "Passwords Unmatched.")
            return redirect("UserProfile")
        if check_password(oldpass, request.user.password):
            userdet = User.objects.get(username=email)
            userdet.set_password(newpass)
            userdet.save()
            userDet = User.objects.get(username=email)
            login(request, userDet)
            sendEmail(request.user.first_name, request.user.username, "Password Changed", "We are pleased to inform you that your request to change your Articles account password has been processed. Your proactive approach to account security is commendable, and we thank you for taking the necessary steps to safeguard your information. Should you encounter any issues or have any concerns, please feel free to reach out to us for assistance. Thank you for entrusting us with your online presence, and we remain committed to providing you with a secure and reliable platform for your blogging endeavors.")
            messages.success(request, "Your password has been changed.")
        else:
            messages.warning(request, "Incorrect password entered.")
        return redirect("UserProfile")
    return redirect("ErrorPage")

def PostComment(request):
    if request.method == "POST":
        editPhoto = ProfilePhoto.objects.get(UserDetails = User.objects.get(username = request.user.username))
        comment = request.POST["comment"]
        name = request.user.first_name
        email = request.user.username
        blogid = request.POST["id"]
        userdet = User.objects.get(username=email)
        blogdet = Blog.objects.get(id = blogid)
        postComment = BlogComment(UserDetails = userdet, Name = name, Email = email, BlogDetails = blogdet, Comment = comment, User_ProfilePhoto = editPhoto.Photo)
        postComment.save()
        messages.success(request, "Your comment has been posted.")
        return redirect(f"read-blog/{blogdet.BlogSlug}")
    return redirect("ErrorPage")

def Search(request):
    search_text = request.GET["search"]
    searching = Blog.objects.filter(BlogName__icontains = search_text) or Blog.objects.filter(BlogDescription__icontains = search_text) or Blog.objects.filter(BlogCategory__icontains = search_text) or Blog.objects.filter(BlogPost__icontains = search_text)
    return render(request, "search.html", {"searchdata" : searching, "search_text" : search_text, "searchcount" : searching.count(), "blogs" : Blog.objects.all()[Blog.objects.count() - (Blog.objects.count() - 1):Blog.objects.count():-1]})

def LikeBlog(request, likeid):
    blogdet = Blog.objects.get(id=likeid)
    if blogdet.Likes.filter(username = request.user).exists():
        blogdet.Likes.remove(request.user)
        messages.warning(request, "Your like has been removed.")
        return redirect(f"/read-blog/{blogdet.BlogSlug}")
    blogdet.Likes.add(request.user)
    blogdet.save()
    messages.success(request, "Thank you for liking the blog.")
    return redirect(f"/read-blog/{blogdet.BlogSlug}")

def Cat(request, catslug):
    searchingcat = Blog.objects.filter(BlogCategory = catslug)
    return render(request, "show category.html", {"cattext" : catslug, "carresult" : searchingcat, "blogs" : Blog.objects.all()[Blog.objects.count() - (Blog.objects.count() - 1):Blog.objects.count():-1], "keywords" : catslug})

def PasswordRecovery(request):
    if request.method == "POST":
        email = request.POST["email"]
        if User.objects.filter(username=email).exists() == False:
            messages.warning(request, "This email address is not registered with us.")
            return redirect("ForgotPassword")
        userdet = User.objects.get(username = email)
        cforgotpass = ForgottenPassword(UserDetails = userdet, OTP = user_otp)
        cforgotpass.save()
        forgotpass = ForgottenPassword.objects.filter(UserDetails = userdet).last()
        sendEmail(userdet.first_name, email, "Password Recovery - Articles", f"Thank you for requesting an OTP for password recovery. This happens sometimes that we forgot our passwords of some useful sites like Articles. Your OTP is {forgotpass.OTP}")
        messages.success(request, "Your password recovery OTP has been shared with you.")
        return render(request, "forgot password.html", {"email" : forgotpass.UserDetails.username})
    return redirect("ErrorPage")

def ForgotPassword(request):
    if request.user.is_authenticated == False:
        return render(request, "forgot password.html")
    return redirect("ErrorPage")

def PasswordRecovered(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        userdet = User.objects.get(username = email)
        forgdet = ForgottenPassword.objects.filter(UserDetails = userdet).last()
        if pass1 != pass2:
            messages.warning(request, "Passwords Unmatched.")
            return render(request, "forgot password.html", {"email" : forgdet.UserDetails.username})
        if otp == forgdet.OTP:
            userdet.set_password(pass1)
            userdet.save()
            sendEmail(userdet.first_name, userdet.username, "Password Recovered", "This is to inform you that your Articles account password has been recovered. Thank you.")
            messages.success(request, "Your password has been recovered.")
            return redirect("HomePage")
        else:
            messages.warning(request, "Incorrect OTP entered.")
            return render(request, "forgot password.html", {"email" : forgdet.UserDetails.username})

    return redirect("ErrorPage")

def handle500(request):
    return render(request, "500 error.html")

def handle404(request, exception):
    return render(request, "404 error.html")

def TermsConditions(request):
    return render(request, "terms and conditions.html")

def FC(request):
    return render(request, "fc.html")