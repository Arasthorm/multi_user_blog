#!/usr/bin/env python
# 
# The main html structure and css styling used, were provided by the backend course 
#


import os
import webapp2
import jinja2
import re

import security_functions as s_func
import verification_functions as v_func
import database_functions as d_func

template_dir = os.path.join(os.path.dirname(__file__),'my_templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)
curr_user = ""

class Handler(webapp2.RequestHandler):

	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **params):
		self.write(self.render_str(template, **params))

class SignupHandler(Handler):

	def get(self):
		self.render("signup.html")
	def post(self):

		have_error = 0

		error_username = ""
		error_password = ""
		error_valid = ""
		error_email = ""
		
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")

		if not v_func.valid_username(username):
			have_error = 1
			error_username = "That's not a valid username."
		
		if not v_func.valid_password(password):
			error_password = "That wasn't a valid password."
			have_error = 1
		else:
			if not v_func.valid_validation(password,verify):
				have_error = 1
				error_valid = "Your passwords didn't match."
		if email:
			if not v_func.valid_email(email):
				error_email = "That's not a valid email."
				have_error = 1;

		if v_func.already_exists_username(username):
				have_error = 1
				error_username = "username already exists" 

		if have_error == 0:

			password = s_func.secure_pass(username,password,5)
			user = d_func.Credentials.register_user(username,password) 
			user.put()
			s_func.set_secure_cookie(self,str(user.key().id()))		

			self.redirect("/blog/welcome")
		else:
			self.render("signup.html",error_username=error_username,error_password=error_password,error_valid=error_valid,
					error_email=error_email)

class LoginHandler(Handler):
	def get(self):
		self.render("login.html")
	
	def post(self):
		have_error = 0
		error_msg = ""
		
		username = self.request.get("username")
		password = self.request.get("password")
		
		if not v_func.valid_username(username) and not v_func.valid_password(password):
			have_error = 1
		else: 
			my_cred = d_func.Credentials.get_username_by_name(username) 

			if my_cred and s_func.verify_pass(username,password,my_cred.password):
				
				user_id = my_cred.key().id()
				new_cookie_val = s_func.set_secure_cookie(self,str(user_id))
				self.redirect("/blog/welcome")

			else:
				have_error = 1

		if have_error == 1:
			error_msg = "Invalid login"
			self.render("login.html",error_msg=error_msg)


class WelcomeHandler(Handler):

	def get(self):
		
		username = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))

		if v_func.valid_username(username):
			self.render("welcome.html",username = username)
		else:
			self.redirect("/blog/signup")

class BlogHandler(Handler):

	def get(self):
		#self.response.headers['Content-Type']='text/plain')
		n=0
		last_posts_ids = []
		last_posts = []
		num_comments = []
		
		posts = d_func.Post.get_all_posts_cronologically()
		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))

		for post in posts:
			
			last_posts.append(post)
			ID = str(post.key().id())
			last_posts_ids.append(ID)
			num_comments.append(d_func.Comment.get_all_post_comments(ID).count())

		post_id = self.request.get("post_id")
		if post_id:
			
			users_liked_post = d_func.Like.get_users_liked_post(post_id)
			if not curr_user in users_liked_post and not d_func.Post.check_author_post(curr_user,post_id):


				post = d_func.Post.get_post(post_id)
				post.num_likes = str(int(post.num_likes) + 1)

				post.put()
				like = d_func.Like.add_like(post_id,curr_user)
				like.put()

		self.render("blog.html",user=curr_user,posts=last_posts,last_posts_ids=last_posts_ids,n=len(last_posts), 
					num_comments = num_comments)

class NewPostHandler(Handler):
	
	def get(self):
		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))
		if s_func.read_secure_cookie(self) == "":
			self.redirect("/blog/signup")
		else:
			self.render("newpost.html",user=curr_user,type_post="New Post")

	def post(self):
		
		subject = self.request.get("subject")
		content = self.request.get("content")
		author = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))

		if subject and content:

			p = d_func.Post.register_post(subject,content,author,str(0)) 
			p.put()

			self.redirect("/blog/"+str(p.key().id()))
		else:
			error = "You need to put valid subject and content"
			self.render('newpost.html',user=curr_user,subject=subject,content=content,error=error)

class Posted(Handler):
	def get(self,post_id):

		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))
		post = d_func.Post.get_post(post_id)
		comments = d_func.Comment.get_all_post_comments(post_id)
		author_post = d_func.Post.get_author_post(post_id)

		if not post:
			self.error(404)
			return
		self.render("posted.html",user=curr_user,post=post,post_id=post_id,author_post=author_post,comments=comments)

	def post(self,post_id):

		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))
		post = d_func.Post.get_post(post_id)
		author_post = d_func.Post.get_author_post(post_id)


		comment = self.request.get("comment")

		if not comment == "" and not curr_user == "":
			store_comment = d_func.Comment.add_comment(post_id,comment,curr_user)
			store_comment.put()
			error= ""
		else:
			error = "Not able to comment" 

		comments = d_func.Comment.get_all_post_comments(post_id)
		self.render("posted.html",user=curr_user,post=post,post_id=post_id,author_post=author_post,comments=comments,error=error)


class EditPostHandler(Handler):
	def get(self,post_id):
		
		post = d_func.Post.get_post(post_id)
		subject = post.subject
		content = post.content 

		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))

		error = ""
		if d_func.Post.check_author_post(curr_user,post_id):
			self.render('newpost.html',post_id=post_id,user=curr_user,type_post="Edit Post",subject=subject,content=content,error=error)
		else:
			self.redirect("/blog")
			
	def post(self,post_id):
		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:

			post = d_func.Post.get_post(post_id)
			post.subject = subject
			post.content = content
			post.put()
			self.redirect("/blog/"+post_id)
		else:
			error = "You need to put valid subject and content"
			self.render('newpost.html',post_id=post_id,type_post="Edit Post",user=curr_user,subject=subject,content=content,error=error)

class DeletePostHandler(Handler):
	def get(self,post_id):
		
		post = d_func.Post.get_post(post_id)
		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))

		error = ""

		if d_func.Post.check_author_post(curr_user,post_id):
			self.render("deletepost.html",type_post="Delete post",user=curr_user,post=post,post_id=post_id,error=error)
		else:
			self.redirect("/blog")

	def post(self,post_id):
		post = d_func.Post.get_post(post_id)
		post.delete()
		self.redirect("/blog")

class EditCommentHandler(Handler):
	def get(self,post_id):
		
		c_id = self.request.get("c_ID")
		comment = d_func.Comment.get_comment_byID(c_id)
		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))


		if d_func.Comment.check_author_comment(curr_user,c_id):
			self.render("edit_delete_comment.html",type_post="Edit comment",user=curr_user,comment=comment,post_id=post_id)
		else:
			self.redirect("/blog")

	def post(self,post_id):
	
		content = self.request.get("content")
		c_id = self.request.get("c_ID")
		comment = d_func.Comment.get_comment_byID(c_id)
		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))

		if content:
			comment.comment = content
			comment.put() 
			self.redirect("/blog/"+post_id)
		else:
			error = "No content"
			self.render("edit_delete_comment.html",type_post="Edit comment",user=curr_user,comment=comment,post_id=post_id,error=error)

class DeleteCommentHandler(Handler):
	def get(self,post_id):
		
		c_id = self.request.get("c_ID")
		comment = d_func.Comment.get_comment_byID(c_id)
		curr_user = d_func.Credentials.get_username_by_ID(s_func.read_secure_cookie(self))
		
		if d_func.Comment.check_author_comment(curr_user,c_id):
			self.render("edit_delete_comment.html",type_post="Delete comment",user=curr_user,comment=comment,post_id=post_id)
		else:
			self.redirect("/blog")

	def post(self,post_id):

		c_id = self.request.get("c_ID")
		comment = d_func.Comment.get_comment_byID(c_id)
		comment.delete()

		self.redirect("/blog/"+post_id)



class MainHandler(Handler):
	def get(self):
		self.redirect("/blog")


class LogoutHandler(Handler):
	def get(self):
		logout = ""
		self.response.headers.add_header("Set-Cookie",'user_id=%s;Path=/' % logout)	
		self.redirect("/blog/login")



app = webapp2.WSGIApplication([
   								('/',MainHandler),
   								('/blog',BlogHandler),
   								('/blog/newpost',NewPostHandler),
   								('/blog/editpost/([0-9]+)',EditPostHandler),
   								('/blog/editcomment/([0-9]+)',EditCommentHandler),
   								('/blog/deletecomment/([0-9]+)',DeleteCommentHandler),
   								('/blog/deletepost/([0-9]+)',DeletePostHandler),
   								('/blog/([0-9]+)', Posted),
   								('/blog/signup',SignupHandler),
   								('/blog/welcome',WelcomeHandler),
   								('/blog/login',LoginHandler),
   								('/blog/logout',LogoutHandler)
], debug=True)
