import os
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Optional, Tuple, Union
from langchain.docstore.document import Document
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores.utils import DistanceStrategy, maximal_marginal_relevance
import numpy as np
import json
import logging
import uuid
from langchain.utils.iter import batch_iterate
try:
    from script import export
except:
    pass

logger = logging.getLogger(__name__)

class VectorStore(Pinecone):
    REQUEST_TIMEOUT=10
    INDEX_NAME = "jarvis"
    NAMESPACE = "filecoin"

    def __init__(self) -> None:
        # pinecone.init(
        #     api_key=os.getenv("PINECONE_API_KEY"),  
        #     environment=os.getenv("PINECONE_ENV"),  
        # )
        pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        self.dims = 1536
        index = pc.Index(self.INDEX_NAME)
        super().__init__(index, OpenAIEmbeddings(),"text")  

    def add_docs(self,docs):
        Pinecone.from_documents(docs, self.embeddings, index_name=self.INDEX_NAME)

    def search(self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None,
        namespace: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Return pinecone documents most similar to query.

        Args:
            query: Text to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            filter: Dictionary of argument(s) to filter on metadata
            namespace: Namespace to search in. Default will search in '' namespace.

        Returns:
            List of Documents most similar to the query and score for each
        """
        docs_and_scores = self.similarity_search_by_vector_with_score(
            self._embed_query(query), k=k, filter=filter, namespace=namespace
        )
        return [doc for doc, _ in docs_and_scores]

    def marginal_search(self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: Optional[dict] = None,
        namespace: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs selected using the maximal marginal relevance.

        Maximal marginal relevance optimizes for similarity to query AND diversity
        among selected documents.

        Args:
            query: Text to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            fetch_k: Number of Documents to fetch to pass to MMR algorithm.
            lambda_mult: Number between 0 and 1 that determines the degree of diversity among the results with 0 corresponding
                        to maximum diversity and 1 to minimum diversity.
                        Defaults to 0.5.
        Returns:
            List of Documents selected by maximal marginal relevance.
        """
        embedding = self._embed_query(query)
        return self.max_marginal_relevance_search_by_vector(
            embedding, k, fetch_k, lambda_mult, filter, namespace
        )
        
    def jsonfy(self,docs):
        docs = [doc.dict() for doc in docs]
        docs = json.dumps(docs)
        return docs

    def similarity_search_by_vector_with_score(
        self,
        embedding: List[float],
        *,
        k: int = 4,
        filter: Optional[dict] = None,
        namespace: Optional[str] = None,
    ) -> List[Tuple[Document, float]]:
        """Return pinecone documents most similar to embedding, along with scores."""

        if namespace is None:
            namespace = self._namespace
        docs = []
        results = self._index.query(
            vector=[embedding],
            top_k=k,
            include_metadata=True,
            namespace=namespace,
            filter=filter,
            _request_timeout=self.REQUEST_TIMEOUT
        )
        for res in results["matches"]:
            metadata = res["metadata"]
            if self._text_key in metadata:
                text = metadata.pop(self._text_key)
                score = res["score"]
                metadata['score'] = score
                # print(f"metadata {metadata}")
                docs.append((Document(page_content=text, metadata=metadata), score))
            else:
                logger.warning(
                    f"Found document with no `{self._text_key}` key. Skipping."
                )
        return docs
    
    def max_marginal_relevance_search_by_vector(
        self,
        embedding: List[float],
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: Optional[dict] = None,
        namespace: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs selected using the maximal marginal relevance.

        Maximal marginal relevance optimizes for similarity to query AND diversity
        among selected documents.

        Args:
            embedding: Embedding to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            fetch_k: Number of Documents to fetch to pass to MMR algorithm.
            lambda_mult: Number between 0 and 1 that determines the degree
                        of diversity among the results with 0 corresponding
                        to maximum diversity and 1 to minimum diversity.
                        Defaults to 0.5.
        Returns:
            List of Documents selected by maximal marginal relevance.
        """
        if namespace is None:
            namespace = self._namespace
        results = self._index.query(
            vector=[embedding],
            top_k=fetch_k,
            include_values=True,
            include_metadata=True,
            namespace=namespace,
            filter=filter,
            _request_timeout=self.REQUEST_TIMEOUT
        )
        mmr_selected = maximal_marginal_relevance(
            np.array([embedding], dtype=np.float32),
            [item["values"] for item in results["matches"]],
            k=k,
            lambda_mult=lambda_mult,
        )
        selected = []
        for i in mmr_selected:
            metadata = results["matches"][i]["metadata"]
            score = results["matches"][i]["score"]
            metadata['score'] = score
            selected.append(metadata)
        # selected = [results["matches"][i]["metadata"] for i in mmr_selected]
        return [
            Document(page_content=metadata.pop((self._text_key)), metadata=metadata)
            for metadata in selected
        ]

    def upsert(self,text,id,source=''):
        embed = self.embeddings.embed_query(text)
        metadata = {"description":text,"text":text,"source":source}
        vector_store._index.update(id=id,values=embed,set_metadata=metadata)
        # vector_store._index.upsert(vectors=[
        #     {'id':id,'values':embed,'metadata':metadata}]
        # )
        print(f"upsert text:{text} with meta:{metadata}")

vector_store = VectorStore()