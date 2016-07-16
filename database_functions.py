from google.appengine.ext import db

class Credentials(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)

    @classmethod
    def register_user(cls, username, password):
        c = Credentials(username=username, password=password)
        return c

    @classmethod
    def get_username_by_ID(cls, user_id):
        if not user_id == "":
            username = cls.get_by_id(int(user_id)).username
            return username
        else:
            return ""

    @classmethod
    def get_username_by_name(cls, username):
        cred_username = db.GqlQuery(
            "SELECT * FROM Credentials WHERE username = :user", user=str(username)).get()
        return cred_username

    @classmethod
    def get_all_credentials(cls):
        creds = db.GqlQuery("SELECT * FROM Credentials")
        return creds


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    num_likes = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def register_post(cls, subject, content, author, num_likes):
        post = Post(
            subject=subject, content=content, author=author, num_likes=num_likes)
        return post

    @classmethod
    def check_author_post(cls, author, post_id):

        """
        Compares the current user logged with the author of the post

        Args:
            author : The author of the post
            post_id : Id of the post

        Returns:
                A boolean depending if the username is the same as the author 

        """

        post = Post.get_by_id(int(post_id))
        return True if post.author == author else False

    @classmethod
    def get_post(cls, post_id):
        post = Post.get_by_id(int(post_id))
        return post

    @classmethod
    def get_all_posts_cronologically(cls):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC limit 10")
        return posts

    @classmethod
    def get_author_post(cls, post_id):
        post = Post.get_by_id(int(post_id))
        return post.author


class Comment(db.Model):
    post_id = db.StringProperty(required=True)
    comment = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def add_comment(cls, post_id, comment, author):
        comment = Comment(post_id=post_id, comment=comment, author=author)
        return comment

    @classmethod
    def get_all_post_comments(cls, post_ID):
        comments = db.GqlQuery(
            "SELECT * FROM Comment WHERE post_id = :post_ID ORDER BY created DESC", post_ID=post_ID)
        return comments

    @classmethod
    def get_comment_byID(cls, ID):
        comment = Comment.get_by_id(int(ID))
        return comment

    @classmethod
    def check_author_comment(cls, author, com_id):
        comment = Comment.get_by_id(int(com_id))
        return True if comment.author == author else False

class Like(db.Model):
    post_id = db.StringProperty(required=True)
    upvote_author = db.StringProperty(required=True)

    @classmethod
    def add_like(cls, post_id, user):
        like = Like(post_id=post_id, upvote_author=user)
        return like

    @classmethod
    def get_users_liked_post(cls, ID):

        users = []
        likes = db.GqlQuery("SELECT * FROM Like WHERE post_id = :ID", ID=ID)
        for l in likes:
            users.append(l.upvote_author)
        return users
