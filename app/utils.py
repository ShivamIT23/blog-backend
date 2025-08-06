from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain:str, hashed:str):
    return pwd_context.verify(plain,hashed)

def replace_nbsp_in_post(post: dict) -> dict:
    """
    Replace all occurrences of '&nbsp;' with a space in the 'title' and 'content' fields of a post dict.
    Returns the modified dict.
    """
    if 'title' in post and isinstance(post['title'], str):
        post['title'] = post['title'].replace('&nbsp;', ' ')
    if 'content' in post and isinstance(post['content'], str):
        post['content'] = post['content'].replace('&nbsp;', ' ')
    return post

   
