from typing import List, Dict, Any
from crawler.extractor.models import PageData
from crawler.workflow.models import Workflow
from crawler.forms.models import SemanticForm
from .embedder import SemanticEmbedder
from .vector_store import VectorStore
from shared.logger import get_logger

logger = get_logger(__name__)

class KnowledgeIndexer:
    """Orchestrates embedding generation and vector storage for crawler data."""
    
    def __init__(self, embedder: SemanticEmbedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def index_page(self, page: PageData, state_id: str):
        """Indexes a page's metadata and structure."""
        # Create a descriptive text document representing this page
        interactive_roles = set([c.role for c in page.components if c.role])
        content_summary = f"Page Title: {page.title}. URL: {page.url}. "
        content_summary += f"This page allows actions like: {', '.join(list(interactive_roles)[:10])}."
        
        doc = {
            "type": "page",
            "state_id": state_id,
            "url": page.url,
            "title": page.title,
            "text": content_summary
        }
        
        emb = self.embedder.embed_batch([content_summary])
        self.vector_store.add_documents([doc], emb)
        
    def index_workflow(self, workflow: Workflow):
        """Indexes a workflow to make its task semantically searchable."""
        step_descriptions = []
        for step in workflow.steps:
            step_descriptions.append(f"Click '{step.action.label}'")
            
        content_summary = f"Workflow Task: {workflow.inferred_task}. "
        content_summary += f"Steps to accomplish this: {' -> '.join(step_descriptions)}."
        
        doc = {
            "type": "workflow",
            "workflow_id": workflow.id,
            "task": workflow.inferred_task,
            "text": content_summary
        }
        
        emb = self.embedder.embed_batch([content_summary])
        self.vector_store.add_documents([doc], emb)

    def index_form(self, form: SemanticForm, source_url: str):
        """Indexes a semantic form."""
        field_names = [f.logical_label or f.name for f in form.fields]
        
        content_summary = f"Form Intent: {form.intent}. "
        content_summary += f"Requires fields: {', '.join(field_names)}."
        
        doc = {
            "type": "form",
            "form_id": form.id,
            "intent": form.intent,
            "source_url": source_url,
            "text": content_summary
        }
        
        emb = self.embedder.embed_batch([content_summary])
        self.vector_store.add_documents([doc], emb)
