from enum import Enum  # Correct import for Enum
from pydantic import BaseModel, Field, EmailStr, HttpUrl, root_validator
from bson import ObjectId
from typing import List, Optional, Dict, Literal  # Keep these imports from typing
from datetime import datetime
from typing import Any
from typing import Annotated, Union


# Custom validator for ObjectId, represented as a string in the model
def pyobjectid_validator(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")
    return ObjectId(value)


PyObjectId = Annotated[
    str, Field(alias="_id", default_factory=ObjectId), pyobjectid_validator
]


class MongoModel(BaseModel):
    # id: Optional[PyObjectId] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class Webhook(MongoModel):
    type: str
    payload_url: HttpUrl
    events: List[str]


class Branch(MongoModel):
    name: str
    repo_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.now)
    modified_by_projectx: bool = Field(default=False)


class Commit(MongoModel):
    sha: str
    branch_id: PyObjectId
    ai_session_id: PyObjectId
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ActionType(Enum):
    NAVIGATION = "navigation"
    SUGGESTION = "suggestion"


class Action(MongoModel):
    text: str
    value: str
    type: ActionType


class Message(MongoModel):
    sender: str
    text: str
    actions: List[Action]
    created_at: datetime = Field(default_factory=datetime.now)


class Question(MongoModel):
    tag: str
    question: str
    answer: str
    choices: Dict[str, List[str]]


class ConsultScaffold(MongoModel):
    objective: str
    questions: List[Question]


StatusValue = Literal["not_started", "in_progress", "completed"]
GenerationKey = Literal["input", "output"]
RequirementType = Literal["technical", "non_technical"]


class Task(MongoModel):
    name: str
    description: str
    status: StatusValue


class ChatRequest(BaseModel):
    """Request model for chat requests.
    Includes the conversation ID and the message from the user.
    """

    session_id: str
    message: str


class Message(BaseModel):
    role: str
    content: str


class Conversation(BaseModel):
    conversation: List[Message]


class AISession(BaseModel):
    user_id: str
    # Lifecycle
    status: StatusValue = "in_progress"
    stages: Dict[str, StatusValue] = {
        "consult": "not_started",
        "planning": "not_started",
        "coding": "not_started",
    }

    # Consult
    title: Optional[str] = None
    description: Optional[str] = None
    message_history: Conversation = []  # Chat history
    tasks: List[Task] = []
    requirements: Dict[RequirementType, List[Any]] = {
        "technical": [],
        "non_technical": [],
    }

    # Generation Data
    generated_code: Dict[GenerationKey, Any] = {
        "input": None,
        "output": None,
    }  # Generation data

    # Git & Repo Details
    output_branch: Optional[str] = None
    output_commit: Optional[str] = None  # Assuming Commit is a string or similar
    repository_name: Optional[str] = None  # Name of the repository
    repository_description: Optional[str] = None  # Description of the repository

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


RepoVisibility = Literal["public", "private"]


class Repository(MongoModel):
    user_id: str
    name: Optional[str] = None
    is_created_on_github: bool = False  # Is the repo created in GitHub2
    default_branch: str = "main"  # Default branch of the repo
    html_url: Optional[HttpUrl] = None  # URL of the repo
    url: Optional[HttpUrl] = None  # API URL of the repo
    commits_url: Optional[HttpUrl] = None  # API URL of the commits
    branches_url: Optional[HttpUrl] = None  # API URL of the branches
    description: Optional[str] = None  # Description of the repo
    language: Optional[str] = None  # Language of the repo
    frameworks: Optional[str] = None  # Frameworks used in the repo
    visibliity: Optional[RepoVisibility] = "private"  # Visibility of the repo

    # Vector Storage Details
    is_indexed: bool = False  # Is the repo indexed in Pinecone
    is_outdated: bool = False  # Is the repo outdated in Pinecone
    last_indexed: Optional[datetime] = None  # Last indexed time
    pinecone_index_info: Optional[str] = None  # Pinecone index info

    # Uncomment and define AISession if needed
    # ai_sessions: List[AISession]

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Add validator that maps _id to id
    # @validator("id", pre=True)
    # def id_str(cls, v):
    #     return str(v) if v is not None else v


class RateLimit(MongoModel):
    limit: int
    remaining: int
    reset: datetime


class User(MongoModel):
    name: str
    email: EmailStr
    image: Optional[str] = None
    customerId: Optional[str] = None
    priceId: Optional[str] = None
    hasAccess: bool = False
    github_app_installation_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    oauth_expiration: Optional[datetime] = None
    roles: Optional[List[str]] = None
    rate_limit: Optional[RateLimit] = None
    # projects: List[Project]
    oauth_scopes: List[str]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class SessionModel:
    def __init__(self, db):
        self.db = db
        self._collection = None

    @property
    def collection(self):
        if not self._collection:
            self._collection = self.db["sessions"]
        return self._collection

    async def create_session(self, session_data):
        await self.collection.insert_one(session_data)


class StartupRequest(MongoModel):
    idea: str
    investment: float = 3.0
    n_round: int = 2
    code_review: bool = True
    run_tests: bool = False
    implement: bool = True
    project_name: str = ""
    inc: bool = False
    project_path: str = ""
    reqa_file: str = ""
    max_auto_summarize_code: int = -1


class GenerationRequest(MongoModel):
    projectName: Optional[str]
    idea: str
    appType: str
    technology: List[str]
    additionalDetails: Optional[str]


class Technology(MongoModel):
    frameworks: List[str]
    languages: List[str]


class ProjectData(MongoModel):
    technologies: Technology
    capabilities: List[str]


class SubmissionData(MongoModel):
    prompt: str
    isNewRepository: bool
    technologies: Technology


class Code(MongoModel):
    filename: str
    contents: str


class GenerationData(MongoModel):
    summary: str
    tasks: str
    code: List[Code]


class Change(MongoModel):
    fileName: str
    changeType: Union[Literal["A"], Literal["M"], Literal["D"]]


class GitData(MongoModel):
    branch: str
    commitId: str
    commitMessage: str
    changes: List[Change]


class MetaData(MongoModel):
    total_cost: int
    total_tasks: int
    total_revisions: int
    total_time: int


class GenerationDataObject(MongoModel):
    projectData: ProjectData
    submissionData: SubmissionData
    generationData: GenerationData
    gitData: GitData
    metaData: MetaData
