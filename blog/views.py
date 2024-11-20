
from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView ,DetailView
from django.views.generic import View
from django.http import HttpResponseRedirect 
from django.urls import reverse
from .models import Post
from .forms import CommentForm
class IndexPage(ListView):
    template_name = "blog/index.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "posts"
    
    def get_queryset(self):
        query_set =  super().get_queryset()
        data = query_set[:3]
        return data

# # Create your views here.
# def index_page(request): 
#     latest_posts = Post.objects.all().order_by("-date")[:3]
#     return render(request ,"blog/index.html" , {
#         "posts":latest_posts
#     })



class AllPosts(ListView):
    template_name = "blog/allposts.html"
    model = Post
    ordering =["-date"]
    context_object_name = "allposts"



# def posts(request):
#     all_posts = Post.objects.all().order_by("-date")
#     return render(request,"blog/allposts.html" ,{
#         "all_posts" : all_posts
#     })




class SinglePostView(DetailView):
    # template_name = "blog/post-detail.html"
    # model = Post

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["post_tags"] = self.object.tags.all()
    #     context["comment_form"] =CommentForm
    #     return context
    def is_stored_post(self,request,post_id):
        stored_posts  = request.session.get("stored-posts")
        if stored_posts is not None:
            is_saved_for_later = post_id in stored_posts
        else:
            is_saved_for_later = False
        return is_saved_for_later



    def get(self,request,slug):
        post = Post.objects.get(slug=slug)
        
        context ={
            "post":post,
            "post_tags":post.tags.all(),
            "comment_form":CommentForm(),
            "allthecomments":post.comments.all().order_by("-id"),
            "saved_for_later":self.is_stored_post(request,post.id)
        }
        return render(request , "blog/post-detail.html",context)
    

    def post(self,request,slug):
        comment_form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)
        if comment_form.is_valid():
            allcomments =comment_form.save(commit=False)
            allcomments.postof = post
            allcomments.save()
            return HttpResponseRedirect(reverse("post-detail-page",args=[slug]))
            
        context ={
            "post":post,
            "post_tags":post.tags.all(),
            "comment_form":CommentForm(),
            "allthecomments":post.comments.all().order_by("-id"), 
            "saved_for_later":self.is_stored_post(request,post.id)
        }
        return render(request,"blog/post-detail.html",context)
    

# def post_detail(request , slug):
#     identified_post = get_object_or_404(Post,slug=slug)
#     return render(request,"blog/post-detail.html" , 
#                   {
#                     "post":identified_post,
#                     "post_tags":identified_post.tags.all()
#                   })


# class ReadLaterView(View):
#     def post(self,request):
#         stored_posts = request.session.get("stored_posts")

#         if(stored_posts is None):
#             stored_posts = []

#         post_id =int(request.POST["post_id"])

#         if post_id not in stored_posts:
#             stored_posts.append(post_id)
            
        
#         return HttpResponseRedirect("/")


class ReadLaterView(View):
    def get(self, request):
        # Retrieve stored posts from session
        stored_posts = request.session.get("stored_posts", [])

        # Initialize the context dictionary
        context = {}

        # If no stored posts are present, set the context variables accordingly
        if not stored_posts:
            context["posts"] = []
            context["has_posts"] = False
        else:
            # Fetch the posts from the database
            posts = Post.objects.filter(id__in=stored_posts)
            context["posts"] = posts
            context["has_posts"] = True

        # Render the template with the context
        return render(request, "blog/stored-posts.html", context)

    def post(self, request):
        # Retrieve stored posts from session
        stored_posts = request.session.get("stored_posts", [])

        # Get post_id from POST data, defaulting to None if it's missing
        post_id = request.POST.get("post_id")

        # If post_id is provided and not already stored, add it to the list
        if post_id:
            post_id = int(post_id)
            if post_id not in stored_posts:
                stored_posts.append(post_id)
                # Store the updated list back into the session
            else:
                stored_posts.remove(post_id)
                request.session["stored_posts"] = stored_posts

        # Redirect the user back to the home page or wherever needed
        return HttpResponseRedirect("/")