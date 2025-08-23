# Tidb
##  TiDBGraphStore #
Bases: `GraphStore`
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/graph.py`

| ```
class TiDBGraphStore(GraphStore):
    def __init__(
        self,
        db_connection_string: str,
        entity_table_name: str = "entities",
        relation_table_name: str = "relations",
    ) -> None:
        # TiDB Serverless clusters have a limitation: if there are no active connections for 5 minutes,
        # they will shut down, which closes all connections, so we need to recycle the connections
        self._engine = create_engine(db_connection_string, pool_recycle=300)
        check_db_availability(self._engine)

        self._entity_table_name = entity_table_name
        self._relation_table_name = relation_table_name
        self._entity_model, self._rel_model = self.init_schema()

    def init_schema(self) -> Tuple[Any, Any]:
        """Initialize schema."""
        Base = declarative_base()

        class EntityModel(Base):
            __tablename__ = self._entity_table_name

            id = Column(Integer, primary_key=True)
            name = Column(String(512), nullable=False)
            created_at = Column(DateTime, nullable=False, server_default=sql.func.now())
            updated_at = Column(
                DateTime,
                nullable=False,
                server_default=sql.func.now(),
                onupdate=sql.func.now(),
            )

        class RelationshipModel(Base):
            __tablename__ = self._relation_table_name

            id = Column(Integer, primary_key=True)
            description = Column(Text, nullable=False)
            subject_id = Column(Integer, ForeignKey(f"{self._entity_table_name}.id"))
            object_id = Column(Integer, ForeignKey(f"{self._entity_table_name}.id"))
            created_at = Column(DateTime, nullable=False, server_default=sql.func.now())
            updated_at = Column(
                DateTime,
                nullable=False,
                server_default=sql.func.now(),
                onupdate=sql.func.now(),
            )

            subject = relationship("EntityModel", foreign_keys=[subject_id])
            object = relationship("EntityModel", foreign_keys=[object_id])

        Base.metadata.create_all(self._engine)
        return EntityModel, RelationshipModel

    @property
    def get_client(self) -> Any:
        """Get client."""
        return self._engine

    def upsert_triplet(self, subj: str, rel: str, obj: str) -> None:
        """Add triplet."""
        with Session(self._engine) as session:
            subj_instance, _ = get_or_create(session, self._entity_model, name=subj)
            obj_instance, _ = get_or_create(session, self._entity_model, name=obj)
            get_or_create(
                session,
                self._rel_model,
                description=rel,
                subject=subj_instance,
                object=obj_instance,
            )

    def get(self, subj: str) -> List[List[str]]:
        """Get triplets."""
        with Session(self._engine) as session:
            rels = (
                session.query(self._rel_model)
                .options(
                    joinedload(self._rel_model.subject),
                    joinedload(self._rel_model.object),
                )
                .filter(self._rel_model.subject.has(name=subj))
                .all()
            )
            return [[rel.description, rel.object.name] for rel in rels]

    def get_rel_map(
        self, subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30
    ) -> Dict[str, List[List[str]]]:
        """Get depth-aware rel map."""
        rel_map: Dict[str, List[List[str]]] = defaultdict(list)
        with Session(self._engine) as session:
            # `raw_rels`` is a list of tuples (depth, subject, description, object), ordered by depth
            # Example:
            # +-------+------------------+------------------+------------------+
            # | depth | subject          | description      | object           |
            # +-------+------------------+------------------+------------------+
            # |     1 | Software         | Mention in       | Footnotes        |
            # |     1 | Viaweb           | Started by       | Paul graham      |
            # |     2 | Paul graham      | Invited to       | Lisp conference  |
            # |     2 | Paul graham      | Coded            | Bel              |
            # +-------+------------------+------------------+------------------+
            raw_rels = session.execute(
                sql.text(
                    rel_depth_query.format(
                        relation_table=self._relation_table_name,
                        entity_table=self._entity_table_name,
                    )
                ),
                {
                    "subjs": subjs,
                    "depth": depth,
                    "limit": limit,
                },
            ).fetchall()
            # `obj_reverse_map` is a dict of sets, where the key is a tuple (object, depth)
            # and the value is a set of subjects that have the object at the previous depth
            obj_reverse_map = defaultdict(set)
            for depth, subj, rel, obj in raw_rels:
                if depth == 1:
                    rel_map[subj].append([subj, rel, obj])
                    obj_reverse_map[(obj, depth)].update([subj])
                else:
                    for _subj in obj_reverse_map[(subj, depth - 1)]:
                        rel_map[_subj].append([subj, rel, obj])
                        obj_reverse_map[(obj, depth)].update([_subj])
            return dict(rel_map)

    def delete(self, subj: str, rel: str, obj: str) -> None:
        """Delete triplet."""
        with Session(self._engine) as session:
            stmt = delete(self._rel_model).where(
                self._rel_model.subject.has(name=subj),
                self._rel_model.description == rel,
                self._rel_model.object.has(name=obj),
            )
            result = session.execute(stmt)
            session.commit()
            # no rows affected, do not need to delete entities
            if result.rowcount == 0:
                return

            def delete_entity(entity_name: str):
                stmt = delete(self._entity_model).where(
                    self._entity_model.name == entity_name
                )
                session.execute(stmt)
                session.commit()

            def entity_was_referenced(entity_name: str):
                return (
                    session.query(self._rel_model)
                    .filter(
                        self._rel_model.subject.has(name=entity_name)
                        | self._rel_model.object.has(name=entity_name)
                    )
                    .one_or_none()
                )

            if not entity_was_referenced(subj):
                delete_entity(subj)
            if not entity_was_referenced(obj):
                delete_entity(obj)

    def query(self, query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any:
        """Query the graph store with statement and parameters."""
        with Session(self._engine) as session:
            return session.execute(query, param_map).fetchall()

```
  
---|---  
###  get_client `property` #
```
get_client: Any

```

Get client.
###  init_schema #
```
init_schema() -> Tuple[Any, Any]

```

Initialize schema.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/graph.py`

| ```
def init_schema(self) -> Tuple[Any, Any]:
    """Initialize schema."""
    Base = declarative_base()

    class EntityModel(Base):
        __tablename__ = self._entity_table_name

        id = Column(Integer, primary_key=True)
        name = Column(String(512), nullable=False)
        created_at = Column(DateTime, nullable=False, server_default=sql.func.now())
        updated_at = Column(
            DateTime,
            nullable=False,
            server_default=sql.func.now(),
            onupdate=sql.func.now(),
        )

    class RelationshipModel(Base):
        __tablename__ = self._relation_table_name

        id = Column(Integer, primary_key=True)
        description = Column(Text, nullable=False)
        subject_id = Column(Integer, ForeignKey(f"{self._entity_table_name}.id"))
        object_id = Column(Integer, ForeignKey(f"{self._entity_table_name}.id"))
        created_at = Column(DateTime, nullable=False, server_default=sql.func.now())
        updated_at = Column(
            DateTime,
            nullable=False,
            server_default=sql.func.now(),
            onupdate=sql.func.now(),
        )

        subject = relationship("EntityModel", foreign_keys=[subject_id])
        object = relationship("EntityModel", foreign_keys=[object_id])

    Base.metadata.create_all(self._engine)
    return EntityModel, RelationshipModel

```
  
---|---  
###  upsert_triplet #
```
upsert_triplet(subj: str, rel: str, obj: str) -> None

```

Add triplet.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/graph.py`

| ```
def upsert_triplet(self, subj: str, rel: str, obj: str) -> None:
    """Add triplet."""
    with Session(self._engine) as session:
        subj_instance, _ = get_or_create(session, self._entity_model, name=subj)
        obj_instance, _ = get_or_create(session, self._entity_model, name=obj)
        get_or_create(
            session,
            self._rel_model,
            description=rel,
            subject=subj_instance,
            object=obj_instance,
        )

```
  
---|---  
###  get #
```
get(subj: str) -> List[List[str]]

```

Get triplets.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/graph.py`

| ```
def get(self, subj: str) -> List[List[str]]:
    """Get triplets."""
    with Session(self._engine) as session:
        rels = (
            session.query(self._rel_model)
            .options(
                joinedload(self._rel_model.subject),
                joinedload(self._rel_model.object),
            )
            .filter(self._rel_model.subject.has(name=subj))
            .all()
        )
        return [[rel.description, rel.object.name] for rel in rels]

```
  
---|---  
###  get_rel_map #
```
get_rel_map(subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30) -> Dict[str, List[List[str]]]

```

Get depth-aware rel map.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/graph.py`

| ```
def get_rel_map(
    self, subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30
) -> Dict[str, List[List[str]]]:
    """Get depth-aware rel map."""
    rel_map: Dict[str, List[List[str]]] = defaultdict(list)
    with Session(self._engine) as session:
        # `raw_rels`` is a list of tuples (depth, subject, description, object), ordered by depth
        # Example:
        # +-------+------------------+------------------+------------------+
        # | depth | subject          | description      | object           |
        # +-------+------------------+------------------+------------------+
        # |     1 | Software         | Mention in       | Footnotes        |
        # |     1 | Viaweb           | Started by       | Paul graham      |
        # |     2 | Paul graham      | Invited to       | Lisp conference  |
        # |     2 | Paul graham      | Coded            | Bel              |
        # +-------+------------------+------------------+------------------+
        raw_rels = session.execute(
            sql.text(
                rel_depth_query.format(
                    relation_table=self._relation_table_name,
                    entity_table=self._entity_table_name,
                )
            ),
            {
                "subjs": subjs,
                "depth": depth,
                "limit": limit,
            },
        ).fetchall()
        # `obj_reverse_map` is a dict of sets, where the key is a tuple (object, depth)
        # and the value is a set of subjects that have the object at the previous depth
        obj_reverse_map = defaultdict(set)
        for depth, subj, rel, obj in raw_rels:
            if depth == 1:
                rel_map[subj].append([subj, rel, obj])
                obj_reverse_map[(obj, depth)].update([subj])
            else:
                for _subj in obj_reverse_map[(subj, depth - 1)]:
                    rel_map[_subj].append([subj, rel, obj])
                    obj_reverse_map[(obj, depth)].update([_subj])
        return dict(rel_map)

```
  
---|---  
###  delete #
```
delete(subj: str, rel: str, obj: str) -> None

```

Delete triplet.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/graph.py`

| ```
def delete(self, subj: str, rel: str, obj: str) -> None:
    """Delete triplet."""
    with Session(self._engine) as session:
        stmt = delete(self._rel_model).where(
            self._rel_model.subject.has(name=subj),
            self._rel_model.description == rel,
            self._rel_model.object.has(name=obj),
        )
        result = session.execute(stmt)
        session.commit()
        # no rows affected, do not need to delete entities
        if result.rowcount == 0:
            return

        def delete_entity(entity_name: str):
            stmt = delete(self._entity_model).where(
                self._entity_model.name == entity_name
            )
            session.execute(stmt)
            session.commit()

        def entity_was_referenced(entity_name: str):
            return (
                session.query(self._rel_model)
                .filter(
                    self._rel_model.subject.has(name=entity_name)
                    | self._rel_model.object.has(name=entity_name)
                )
                .one_or_none()
            )

        if not entity_was_referenced(subj):
            delete_entity(subj)
        if not entity_was_referenced(obj):
            delete_entity(obj)

```
  
---|---  
###  query #
```
query(query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any

```

Query the graph store with statement and parameters.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/graph.py`

| ```
def query(self, query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any:
    """Query the graph store with statement and parameters."""
    with Session(self._engine) as session:
        return session.execute(query, param_map).fetchall()

```
  
---|---  
##  TiDBPropertyGraphStore #
Bases: `PropertyGraphStore`
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
class TiDBPropertyGraphStore(PropertyGraphStore):
    # TiDB does not support graph cypher queries
    supports_structured_queries: bool = False
    supports_vector_queries: bool = True

    def __init__(
        self,
        db_connection_string: str,
        embedding_dim: int = 1536,
        node_table_name: str = "pg_nodes",
        relation_table_name: str = "pg_relations",
        drop_existing_table: bool = False,
        echo_queries: bool = False,
    ) -> None:
        # TiDB Serverless clusters have a limitation: if there are no active connections for 5 minutes,
        # they will shut down, which closes all connections, so we need to recycle the connections
        self._engine = create_engine(
            db_connection_string, pool_recycle=300, echo=echo_queries
        )
        check_db_availability(self._engine, check_vector=True)

        self._embedding_dim = embedding_dim
        self._node_table_name = node_table_name
        self._relation_table_name = relation_table_name
        self._drop_existing_table = drop_existing_table
        self._node_model, self._relation_model = self.init_schema()

    def init_schema(self) -> Tuple:
        """Initialize schema."""
        Base = declarative_base()

        class BaseMixin:
            created_at = Column(DateTime, nullable=False, server_default=sql.func.now())
            updated_at = Column(
                DateTime,
                nullable=False,
                server_default=sql.func.now(),
                onupdate=sql.func.now(),
            )

        class NodeModel(BaseMixin, Base):
            __tablename__ = self._node_table_name
            id = Column(String(512), primary_key=True)
            text = Column(TEXT, nullable=True)
            name = Column(String(512), nullable=True)
            label = Column(String(512), nullable=False, default="node")
            properties = Column(JSON, default={})
            embedding = Column(
                VectorType(self._embedding_dim), comment="hnsw(distance=cosine)"
            )

        class RelationModel(BaseMixin, Base):
            __tablename__ = self._relation_table_name
            id = Column(Integer, primary_key=True)
            label = Column(String(512), nullable=False)
            source_id = Column(String(512), ForeignKey(f"{self._node_table_name}.id"))
            target_id = Column(String(512), ForeignKey(f"{self._node_table_name}.id"))
            properties = Column(JSON, default={})

            source = relationship("NodeModel", foreign_keys=[source_id])
            target = relationship("NodeModel", foreign_keys=[target_id])

        if self._drop_existing_table:
            Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        return NodeModel, RelationModel

    def get(
        self,
        properties: Optional[dict] = None,
        ids: Optional[List[str]] = None,
    ) -> List[LabelledNode]:
        """Get nodes."""
        with Session(self._engine) as session:
            query = session.query(self._node_model)
            if properties:
                for key, value in properties.items():
                    query = query.filter(self._node_model.properties[key] == value)
            if ids:
                query = query.filter(self._node_model.id.in_(ids))

            nodes = []
            for n in query.all():
                if n.text and n.name is None:
                    nodes.append(
                        ChunkNode(
                            id=n.id,
                            text=n.text,
                            label=n.label,
                            properties=remove_empty_values(n.properties),
                        )
                    )
                else:
                    nodes.append(
                        EntityNode(
                            name=n.name,
                            label=n.label,
                            properties=remove_empty_values(n.properties),
                        )
                    )
            return nodes

    def get_triplets(
        self,
        entity_names: Optional[List[str]] = None,
        relation_names: Optional[List[str]] = None,
        properties: Optional[dict] = None,
        ids: Optional[List[str]] = None,
    ) -> List[Triplet]:
        """Get triplets."""
        # if nothing is passed, return empty list
        if not ids and not properties and not entity_names and not relation_names:
            return []

        with Session(self._engine) as session:
            query = session.query(self._relation_model).options(
                joinedload(self._relation_model.source),
                joinedload(self._relation_model.target),
            )
            if ids:
                query = query.filter(
                    self._relation_model.source_id.in_(ids)
                    | self._relation_model.target_id.in_(ids)
                )
            if properties:
                for key, value in properties.items():
                    query = query.filter(
                        (self._relation_model.properties[key] == value)
                        | self._relation_model.source.has(
                            self._node_model.properties[key] == value
                        )
                        | self._relation_model.target.has(
                            self._node_model.properties[key] == value
                        )
                    )
            if entity_names:
                query = query.filter(
                    self._relation_model.source.has(
                        self._node_model.name.in_(entity_names)
                    )
                    | self._relation_model.target.has(
                        self._node_model.name.in_(entity_names)
                    )
                )
            if relation_names:
                query = query.filter(self._relation_model.label.in_(relation_names))

            triplets = []
            for r in query.all():
                source = EntityNode(
                    name=r.source.name,
                    label=r.source.label,
                    properties=remove_empty_values(r.source.properties),
                )
                target = EntityNode(
                    name=r.target.name,
                    label=r.target.label,
                    properties=remove_empty_values(r.target.properties),
                )
                relation = Relation(
                    label=r.label,
                    source_id=source.id,
                    target_id=target.id,
                    properties=remove_empty_values(r.properties),
                )
                triplets.append([source, relation, target])
            return triplets

    def get_rel_map(
        self,
        graph_nodes: List[LabelledNode],
        depth: int = 2,
        limit: int = 30,
        ignore_rels: Optional[List[str]] = None,
    ) -> List[Triplet]:
        """Get depth-aware rel map."""
        triplets = []
        ids = [node.id for node in graph_nodes]

        if not ids:
            return []

        with Session(self._engine) as session:
            result = session.execute(
                sql.text(
                    rel_depth_query.format(
                        relation_table=self._relation_table_name,
                        node_table=self._node_table_name,
                    )
                ),
                {
                    "ids": ids,
                    "depth": depth,
                    "limit": limit,
                },
            )

            keys = result.keys()
            raw_rels = [dict(zip(keys, row)) for row in result.fetchall()]

            ignore_rels = ignore_rels or []
            for row in raw_rels:
                if row["rel_label"] in ignore_rels:
                    continue

                source = EntityNode(
                    id=row["e1_id"],
                    name=row["e1_name"],
                    label=row["e1_label"],
                    properties=json.loads(row["e1_properties"]),
                )
                target = EntityNode(
                    id=row["e2_id"],
                    name=row["e2_name"],
                    label=row["e2_label"],
                    properties=json.loads(row["e2_properties"]),
                )
                relation = Relation(
                    label=row["rel_label"],
                    source_id=source.id,
                    target_id=target.id,
                    properties=json.loads(row["rel_properties"]),
                )
                triplets.append([source, relation, target])
        return triplets

    def upsert_nodes(self, nodes: List[LabelledNode]) -> None:
        """Upsert nodes."""
        entity_list: List[EntityNode] = []
        chunk_list: List[ChunkNode] = []
        other_list: List[LabelledNode] = []

        for item in nodes:
            if isinstance(item, EntityNode):
                entity_list.append(item)
            elif isinstance(item, ChunkNode):
                chunk_list.append(item)
            else:
                other_list.append(item)

        with Session(self._engine) as session:
            # TODO: use upsert instead of get_or_create
            for entity in entity_list:
                entity_instance, _ = get_or_create(
                    session, self._node_model, id=entity.id
                )
                entity_instance.name = entity.name
                entity_instance.label = entity.label
                entity_instance.properties = entity.properties
                entity_instance.embedding = entity.embedding
                session.add(entity_instance)

            for chunk in chunk_list:
                chunk_instance, _ = get_or_create(
                    session, self._node_model, id=chunk.id
                )
                chunk_instance.text = chunk.text
                chunk_instance.label = chunk.label
                chunk_instance.properties = chunk.properties
                chunk_instance.embedding = chunk.embedding
                session.add(chunk_instance)
            session.commit()

    def upsert_relations(self, relations: List[Relation]) -> None:
        """Upsert relations."""
        with Session(self._engine) as session:
            for r in relations:
                get_or_create(
                    session,
                    self._node_model,
                    id=r.source_id,
                )
                get_or_create(
                    session,
                    self._node_model,
                    id=r.target_id,
                )
                relation_instance, _ = get_or_create(
                    session,
                    self._relation_model,
                    label=r.label,
                    source_id=r.source_id,
                    target_id=r.target_id,
                )
                relation_instance.properties = r.properties
                session.add(relation_instance)
                session.commit()

    def delete(
        self,
        entity_names: Optional[List[str]] = None,
        relation_names: Optional[List[str]] = None,
        properties: Optional[dict] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Delete matching data."""
        with Session(self._engine) as session:
            # 1. Delete relations
            relation_stmt = delete(self._relation_model)
            if ids:
                relation_stmt = relation_stmt.filter(
                    self._relation_model.source_id.in_(ids)
                    | self._relation_model.target_id.in_(ids)
                )
            if entity_names:
                relation_stmt = relation_stmt.filter(
                    self._relation_model.source.has(name=entity_names)
                    | self._relation_model.target.has(name=entity_names)
                )
            if relation_names:
                relation_stmt = relation_stmt.filter(
                    self._relation_model.label.in_(relation_names)
                )
            if properties:
                for key, value in properties.items():
                    relation_stmt = relation_stmt.filter(
                        self._relation_model.source.has(
                            self._node_model.properties[key] == value
                        )
                        | self._relation_model.target.has(
                            self._node_model.properties[key] == value
                        )
                    )
            session.execute(relation_stmt)

            # 2. Delete nodes
            entity_stmt = delete(self._node_model)
            if ids:
                entity_stmt = entity_stmt.filter(self._node_model.id.in_(ids))
            if entity_names:
                entity_stmt = entity_stmt.filter(
                    self._node_model.name.in_(entity_names)
                )
            if properties:
                for key, value in properties.items():
                    entity_stmt = entity_stmt.filter(
                        self._node_model.properties[key] == value
                    )
            session.execute(entity_stmt)
            session.commit()

    def structured_query(
        self, query: str, param_map: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Query the graph store with statement and parameters."""
        raise NotImplementedError("TiDB does not support cypher queries.")

    def vector_query(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> Tuple[List[LabelledNode], List[float]]:
        """Query the graph store with a vector store query."""
        with Session(self._engine) as session:
            result = (
                session.query(
                    self._node_model,
                    self._node_model.embedding.cosine_distance(
                        query.query_embedding
                    ).label("embedding_distance"),
                )
                .filter(self._node_model.name.is_not(None))
                .order_by(sql.asc("embedding_distance"))
                .limit(query.similarity_top_k)
                .all()
            )

            nodes = []
            scores = []
            for node, score in result:
                nodes.append(
                    EntityNode(
                        name=node.name,
                        label=node.label,
                        properties=remove_empty_values(node.properties),
                    )
                )
                scores.append(score)
            return nodes, scores

```
  
---|---  
###  init_schema #
```
init_schema() -> Tuple

```

Initialize schema.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
def init_schema(self) -> Tuple:
    """Initialize schema."""
    Base = declarative_base()

    class BaseMixin:
        created_at = Column(DateTime, nullable=False, server_default=sql.func.now())
        updated_at = Column(
            DateTime,
            nullable=False,
            server_default=sql.func.now(),
            onupdate=sql.func.now(),
        )

    class NodeModel(BaseMixin, Base):
        __tablename__ = self._node_table_name
        id = Column(String(512), primary_key=True)
        text = Column(TEXT, nullable=True)
        name = Column(String(512), nullable=True)
        label = Column(String(512), nullable=False, default="node")
        properties = Column(JSON, default={})
        embedding = Column(
            VectorType(self._embedding_dim), comment="hnsw(distance=cosine)"
        )

    class RelationModel(BaseMixin, Base):
        __tablename__ = self._relation_table_name
        id = Column(Integer, primary_key=True)
        label = Column(String(512), nullable=False)
        source_id = Column(String(512), ForeignKey(f"{self._node_table_name}.id"))
        target_id = Column(String(512), ForeignKey(f"{self._node_table_name}.id"))
        properties = Column(JSON, default={})

        source = relationship("NodeModel", foreign_keys=[source_id])
        target = relationship("NodeModel", foreign_keys=[target_id])

    if self._drop_existing_table:
        Base.metadata.drop_all(self._engine)
    Base.metadata.create_all(self._engine)
    return NodeModel, RelationModel

```
  
---|---  
###  get #
```
get(properties: Optional[dict] = None, ids: Optional[List[str]] = None) -> List[LabelledNode]

```

Get nodes.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
def get(
    self,
    properties: Optional[dict] = None,
    ids: Optional[List[str]] = None,
) -> List[LabelledNode]:
    """Get nodes."""
    with Session(self._engine) as session:
        query = session.query(self._node_model)
        if properties:
            for key, value in properties.items():
                query = query.filter(self._node_model.properties[key] == value)
        if ids:
            query = query.filter(self._node_model.id.in_(ids))

        nodes = []
        for n in query.all():
            if n.text and n.name is None:
                nodes.append(
                    ChunkNode(
                        id=n.id,
                        text=n.text,
                        label=n.label,
                        properties=remove_empty_values(n.properties),
                    )
                )
            else:
                nodes.append(
                    EntityNode(
                        name=n.name,
                        label=n.label,
                        properties=remove_empty_values(n.properties),
                    )
                )
        return nodes

```
  
---|---  
###  get_triplets #
```
get_triplets(entity_names: Optional[List[str]] = None, relation_names: Optional[List[str]] = None, properties: Optional[dict] = None, ids: Optional[List[str]] = None) -> List[Triplet]

```

Get triplets.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
def get_triplets(
    self,
    entity_names: Optional[List[str]] = None,
    relation_names: Optional[List[str]] = None,
    properties: Optional[dict] = None,
    ids: Optional[List[str]] = None,
) -> List[Triplet]:
    """Get triplets."""
    # if nothing is passed, return empty list
    if not ids and not properties and not entity_names and not relation_names:
        return []

    with Session(self._engine) as session:
        query = session.query(self._relation_model).options(
            joinedload(self._relation_model.source),
            joinedload(self._relation_model.target),
        )
        if ids:
            query = query.filter(
                self._relation_model.source_id.in_(ids)
                | self._relation_model.target_id.in_(ids)
            )
        if properties:
            for key, value in properties.items():
                query = query.filter(
                    (self._relation_model.properties[key] == value)
                    | self._relation_model.source.has(
                        self._node_model.properties[key] == value
                    )
                    | self._relation_model.target.has(
                        self._node_model.properties[key] == value
                    )
                )
        if entity_names:
            query = query.filter(
                self._relation_model.source.has(
                    self._node_model.name.in_(entity_names)
                )
                | self._relation_model.target.has(
                    self._node_model.name.in_(entity_names)
                )
            )
        if relation_names:
            query = query.filter(self._relation_model.label.in_(relation_names))

        triplets = []
        for r in query.all():
            source = EntityNode(
                name=r.source.name,
                label=r.source.label,
                properties=remove_empty_values(r.source.properties),
            )
            target = EntityNode(
                name=r.target.name,
                label=r.target.label,
                properties=remove_empty_values(r.target.properties),
            )
            relation = Relation(
                label=r.label,
                source_id=source.id,
                target_id=target.id,
                properties=remove_empty_values(r.properties),
            )
            triplets.append([source, relation, target])
        return triplets

```
  
---|---  
###  get_rel_map #
```
get_rel_map(graph_nodes: List[LabelledNode], depth: int = 2, limit: int = 30, ignore_rels: Optional[List[str]] = None) -> List[Triplet]

```

Get depth-aware rel map.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
def get_rel_map(
    self,
    graph_nodes: List[LabelledNode],
    depth: int = 2,
    limit: int = 30,
    ignore_rels: Optional[List[str]] = None,
) -> List[Triplet]:
    """Get depth-aware rel map."""
    triplets = []
    ids = [node.id for node in graph_nodes]

    if not ids:
        return []

    with Session(self._engine) as session:
        result = session.execute(
            sql.text(
                rel_depth_query.format(
                    relation_table=self._relation_table_name,
                    node_table=self._node_table_name,
                )
            ),
            {
                "ids": ids,
                "depth": depth,
                "limit": limit,
            },
        )

        keys = result.keys()
        raw_rels = [dict(zip(keys, row)) for row in result.fetchall()]

        ignore_rels = ignore_rels or []
        for row in raw_rels:
            if row["rel_label"] in ignore_rels:
                continue

            source = EntityNode(
                id=row["e1_id"],
                name=row["e1_name"],
                label=row["e1_label"],
                properties=json.loads(row["e1_properties"]),
            )
            target = EntityNode(
                id=row["e2_id"],
                name=row["e2_name"],
                label=row["e2_label"],
                properties=json.loads(row["e2_properties"]),
            )
            relation = Relation(
                label=row["rel_label"],
                source_id=source.id,
                target_id=target.id,
                properties=json.loads(row["rel_properties"]),
            )
            triplets.append([source, relation, target])
    return triplets

```
  
---|---  
###  upsert_nodes #
```
upsert_nodes(nodes: List[LabelledNode]) -> None

```

Upsert nodes.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
def upsert_nodes(self, nodes: List[LabelledNode]) -> None:
    """Upsert nodes."""
    entity_list: List[EntityNode] = []
    chunk_list: List[ChunkNode] = []
    other_list: List[LabelledNode] = []

    for item in nodes:
        if isinstance(item, EntityNode):
            entity_list.append(item)
        elif isinstance(item, ChunkNode):
            chunk_list.append(item)
        else:
            other_list.append(item)

    with Session(self._engine) as session:
        # TODO: use upsert instead of get_or_create
        for entity in entity_list:
            entity_instance, _ = get_or_create(
                session, self._node_model, id=entity.id
            )
            entity_instance.name = entity.name
            entity_instance.label = entity.label
            entity_instance.properties = entity.properties
            entity_instance.embedding = entity.embedding
            session.add(entity_instance)

        for chunk in chunk_list:
            chunk_instance, _ = get_or_create(
                session, self._node_model, id=chunk.id
            )
            chunk_instance.text = chunk.text
            chunk_instance.label = chunk.label
            chunk_instance.properties = chunk.properties
            chunk_instance.embedding = chunk.embedding
            session.add(chunk_instance)
        session.commit()

```
  
---|---  
###  upsert_relations #
```
upsert_relations(relations: List[Relation]) -> None

```

Upsert relations.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
def upsert_relations(self, relations: List[Relation]) -> None:
    """Upsert relations."""
    with Session(self._engine) as session:
        for r in relations:
            get_or_create(
                session,
                self._node_model,
                id=r.source_id,
            )
            get_or_create(
                session,
                self._node_model,
                id=r.target_id,
            )
            relation_instance, _ = get_or_create(
                session,
                self._relation_model,
                label=r.label,
                source_id=r.source_id,
                target_id=r.target_id,
            )
            relation_instance.properties = r.properties
            session.add(relation_instance)
            session.commit()

```
  
---|---  
###  delete #
```
delete(entity_names: Optional[List[str]] = None, relation_names: Optional[List[str]] = None, properties: Optional[dict] = None, ids: Optional[List[str]] = None) -> None

```

Delete matching data.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
def delete(
    self,
    entity_names: Optional[List[str]] = None,
    relation_names: Optional[List[str]] = None,
    properties: Optional[dict] = None,
    ids: Optional[List[str]] = None,
) -> None:
    """Delete matching data."""
    with Session(self._engine) as session:
        # 1. Delete relations
        relation_stmt = delete(self._relation_model)
        if ids:
            relation_stmt = relation_stmt.filter(
                self._relation_model.source_id.in_(ids)
                | self._relation_model.target_id.in_(ids)
            )
        if entity_names:
            relation_stmt = relation_stmt.filter(
                self._relation_model.source.has(name=entity_names)
                | self._relation_model.target.has(name=entity_names)
            )
        if relation_names:
            relation_stmt = relation_stmt.filter(
                self._relation_model.label.in_(relation_names)
            )
        if properties:
            for key, value in properties.items():
                relation_stmt = relation_stmt.filter(
                    self._relation_model.source.has(
                        self._node_model.properties[key] == value
                    )
                    | self._relation_model.target.has(
                        self._node_model.properties[key] == value
                    )
                )
        session.execute(relation_stmt)

        # 2. Delete nodes
        entity_stmt = delete(self._node_model)
        if ids:
            entity_stmt = entity_stmt.filter(self._node_model.id.in_(ids))
        if entity_names:
            entity_stmt = entity_stmt.filter(
                self._node_model.name.in_(entity_names)
            )
        if properties:
            for key, value in properties.items():
                entity_stmt = entity_stmt.filter(
                    self._node_model.properties[key] == value
                )
        session.execute(entity_stmt)
        session.commit()

```
  
---|---  
###  structured_query #
```
structured_query(query: str, param_map: Optional[Dict[str, Any]] = None) -> Any

```

Query the graph store with statement and parameters.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
def structured_query(
    self, query: str, param_map: Optional[Dict[str, Any]] = None
) -> Any:
    """Query the graph store with statement and parameters."""
    raise NotImplementedError("TiDB does not support cypher queries.")

```
  
---|---  
###  vector_query #
```
vector_query(query: VectorStoreQuery, **kwargs: Any) -> Tuple[List[LabelledNode], List[float]]

```

Query the graph store with a vector store query.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-tidb/llama_index/graph_stores/tidb/property_graph.py`

| ```
def vector_query(
    self, query: VectorStoreQuery, **kwargs: Any
) -> Tuple[List[LabelledNode], List[float]]:
    """Query the graph store with a vector store query."""
    with Session(self._engine) as session:
        result = (
            session.query(
                self._node_model,
                self._node_model.embedding.cosine_distance(
                    query.query_embedding
                ).label("embedding_distance"),
            )
            .filter(self._node_model.name.is_not(None))
            .order_by(sql.asc("embedding_distance"))
            .limit(query.similarity_top_k)
            .all()
        )

        nodes = []
        scores = []
        for node, score in result:
            nodes.append(
                EntityNode(
                    name=node.name,
                    label=node.label,
                    properties=remove_empty_values(node.properties),
                )
            )
            scores.append(score)
        return nodes, scores

```
  
---|---
