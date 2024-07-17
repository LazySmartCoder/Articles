from django.db import models
import datetime
from django.contrib.auth.models import User

class Blog(models.Model):
    cat = (
        ("Top Trends", "Top Trends"),
        ("Failure Chronicles", "Failure Chronicles"),
        ("Entertainment", "Entertainment"),
        ("Shark Tank India", "Shark Tank India"),
        ("Technology", "Technology"),
        ("Good Reads", "Good Reads"),
        ("Python", "Python"),
        ("Business News", "Business News"),
    )
    BlogName = models.CharField(max_length=100, blank=False, default="")
    BlogDescription = models.CharField(max_length=500, blank=False, default="")
    BlogKeywords = models.CharField(max_length = 5000, blank = False, default = "")
    BlogDateAdded = models.CharField(max_length=20, blank=False, default="")
    BlogImage = models.CharField(max_length = 5000, default = "")
    BlogSlug = models.CharField(max_length=400, default="")
    BlogCategory = models.CharField(max_length=100, choices=cat, default="")
    BlogPost = models.TextField(max_length=10000, blank=False, default="")
    BlogAuthor = models.CharField(max_length=50, blank=False, default="")
    Views = models.CharField(max_length=50, blank=False, default="0")
    Likes = models.ManyToManyField(User, related_name="UserLikes", blank=True)

    def __str__(self) -> str:
        return self.BlogName

    def __str__(self) -> str:
        return self.BlogName

class ProfilePhoto(models.Model):
    UserDetails = models.ForeignKey(User, related_name="UserPhoto", on_delete=models.CASCADE)
    Photo = models.ImageField(upload_to = "UserProfilePhoto", default="static/Images/User%20profile.png")

    def __str__(self) -> str:
        return self.UserDetails.first_name    

class BlogComment(models.Model):
    date = datetime.datetime.today().date()
    format_date = date.strftime("%d-%m-20%y")
    UserDetails = models.ForeignKey(User, related_name="CommentsUserDet", on_delete=models.CASCADE)
    Name = models.CharField(max_length=200, default="")
    Email = models.EmailField(max_length=200, default="")
    BlogDetails = models.ForeignKey(Blog, related_name="BlogDet", on_delete=models.CASCADE)
    Comment = models.TextField(max_length=1000, default="")
    Date = models.CharField(default=str(datetime.datetime.now().today()), max_length=40)
    ActualDate = models.CharField(default=format_date, max_length=40)
    User_ProfilePhoto = models.CharField(max_length=200, blank=False, default="")
    
    def __str__(self) -> str:
        return self.Comment
    
class ForgottenPassword(models.Model):
    UserDetails = models.ForeignKey(User, related_name="OTPforpasswordrecovery", on_delete=models.CASCADE)
    OTP = models.CharField(max_length=20, default="")

    def __str__(self) -> str:
        return self.UserDetails.first_name

class PaidPromotion(models.Model):
    CompanyName = models.CharField(max_length = 500, default = "")
    Banner = models.CharField(max_length = 5000, default = "")
    ReadBlogsBanner = models.BooleanField(default = False)

    def __str__(self) -> str:
        return self.CompanyName