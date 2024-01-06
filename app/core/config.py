from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    frontend_url: str = "http://localhost:3000"
    frontend_api_url: str = "http://localhost:8000/api/v1"
    jwt_secret: str
    database_url: str = "mongodb://localhost:27017/projectx"
    github_oauth_client_id: str
    github_oauth_client_secret: str
    github_oauth_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"

    github_app_client_id: str
    github_app_secret: str
    github_app_id: str = "451652"
    github_app_name: str
    github_app_redirect_uri: str = "http://localhost:8000/api/github/callback"
    github_app_private_key: str
    
    pinecone_api_key: str
    pinecone_environment: str
    
    openai_api_key: str
    
    stripe_public_key: str
    stripe_secret_key: str
    

    class Config:
        env_file = ".env"

        # @classmethod
        # def customise_sources(cls, init_settings, env_settings, file_secret_settings):
        #     environment = os.getenv('ENVIRONMENT', 'development')
        #     if environment == 'production':
        #         cls.env_file = '.env.production'
        #     elif environment == 'development':
        #         cls.env_file = '.env.development'
        #     return init_settings, env_settings, file_secret_settings

settings = Settings()
