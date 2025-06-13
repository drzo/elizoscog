;; hypergraph-encoding.scm
;; Cognitive Integration Blueprint: Hypergraph Encoding
;; Encode extracted features as hypernode and establish hyperedges for relationships

(define-module (hypergraph hypergraph-encoding))

(use-modules (ice-9 match)
             (srfi srfi-1)
             (srfi srfi-9)
             (srfi srfi-26)
             (hypergraph extract-features))

;; Hypernode record type
(define-record-type <hypernode>
  (make-hypernode id type content attributes hyperedges)
  hypernode?
  (id hypernode-id)
  (type hypernode-type)           ; 'Feature, 'HybridAgent, 'Repository, etc.
  (content hypernode-content)     ; The actual feature or content
  (attributes hypernode-attributes) ; Metadata and annotations
  (hyperedges hypernode-hyperedges)) ; Connected hyperedges

;; Hyperedge record type  
(define-record-type <hyperedge>
  (make-hyperedge id type nodes attributes weight)
  hyperedge?
  (id hyperedge-id)
  (type hyperedge-type)           ; 'depends-on, 'calls, 'inherits, 'implements, etc.
  (nodes hyperedge-nodes)         ; List of connected hypernode IDs
  (attributes hyperedge-attributes) ; Relationship metadata
  (weight hyperedge-weight))      ; Relationship strength/confidence

;; Hypergraph state
(define-record-type <hypergraph>
  (make-hypergraph nodes edges next-id)
  hypergraph?
  (nodes hypergraph-nodes)        ; Hash table of hypernode-id -> hypernode
  (edges hypergraph-edges)        ; Hash table of hyperedge-id -> hyperedge  
  (next-id hypergraph-next-id))   ; Counter for unique IDs

;; Core hypergraph operations as specified in the blueprint

;; Create new hypergraph
(define (create-hypergraph)
  "Create empty hypergraph"
  (make-hypergraph (make-hash-table) (make-hash-table) 0))

;; Feature to hypernode conversion (main blueprint function)
(define (feature->hypernode feature meta)
  "Convert extracted feature to hypernode representation"
  (let ((id (gensym "node-"))
        (attributes (append 
                      `((name . ,(feature-name feature))
                        (language . ,(feature-language feature))
                        (file . ,(feature-file feature))
                        (line . ,(feature-line feature))
                        (source-repo . ,(assoc-ref meta 'repo))
                        (extraction-time . ,(current-time)))
                      (feature-metadata feature)
                      meta)))
    (make-hypernode
      id
      'Feature
      feature
      attributes
      '())))

;; Link features with hyperedges (main blueprint function)
(define (link-features fn1 fn2 relation . args)
  "Create hyperedge linking two features with specified relation"
  (let ((edge-id (gensym "edge-"))
        (weight (if (null? args) 1.0 (car args)))
        (attributes (if (< (length args) 2) '() (cadr args))))
    (make-hyperedge
      edge-id
      relation
      (list (hypernode-id fn1) (hypernode-id fn2))
      attributes
      weight)))

;; Add hypernode to hypergraph
(define (add-hypernode! hypergraph node)
  "Add hypernode to hypergraph"
  (hash-set! (hypergraph-nodes hypergraph) (hypernode-id node) node)
  (set-hypergraph-next-id! hypergraph (+ (hypergraph-next-id hypergraph) 1))
  node)

;; Add hyperedge to hypergraph
(define (add-hyperedge! hypergraph edge)
  "Add hyperedge to hypergraph and update connected nodes"
  (hash-set! (hypergraph-edges hypergraph) (hyperedge-id edge) edge)
  
  ;; Update connected nodes to reference this edge
  (for-each
    (lambda (node-id)
      (let ((node (hash-ref (hypergraph-nodes hypergraph) node-id)))
        (when node
          (set-hypernode-hyperedges! node 
            (cons (hyperedge-id edge) (hypernode-hyperedges node))))))
    (hyperedge-nodes edge))
  
  edge)

;; Repository feature extraction and encoding
(define (extract-and-encode-repository repo-path repo-meta)
  "Extract features from repository and encode as hypergraph"
  (let ((hypergraph (create-hypergraph))
        (features (extract-features repo-path)))
    
    ;; Convert each feature to hypernode
    (for-each
      (lambda (feature)
        (let ((node (feature->hypernode feature repo-meta)))
          (add-hypernode! hypergraph node)))
      features)
    
    ;; Create dependency edges
    (create-dependency-edges! hypergraph features repo-meta)
    
    ;; Create interface edges  
    (create-interface-edges! hypergraph features repo-meta)
    
    ;; Create data flow edges
    (create-data-flow-edges! hypergraph features repo-meta)
    
    hypergraph))

;; Dependency edge creation
(define (create-dependency-edges! hypergraph features repo-meta)
  "Create hyperedges for dependency relationships"
  (for-each
    (lambda (feature)
      (let ((feature-node (find-node-by-feature hypergraph feature)))
        (when feature-node
          (for-each
            (lambda (dep)
              (let ((dep-node (find-node-by-name hypergraph dep)))
                (when dep-node
                  (let ((edge (link-features feature-node dep-node 'depends-on 
                                           0.8 `((dependency-type . import)))))
                    (add-hyperedge! hypergraph edge)))))
            (feature-dependencies feature)))))
    features))

;; Interface edge creation
(define (create-interface-edges! hypergraph features repo-meta)
  "Create hyperedges for interface relationships"
  ;; Group features by language and create interface connections
  (let ((language-groups (group-features-by-language features)))
    (for-each
      (lambda (lang-group)
        (let ((language (car lang-group))
              (lang-features (cdr lang-group)))
          ;; Create interface edges for same-language features
          (create-language-interface-edges! hypergraph lang-features language)))
      language-groups)))

;; Data flow edge creation
(define (create-data-flow-edges! hypergraph features repo-meta)
  "Create hyperedges for data flow relationships"
  ;; Analyze function call patterns and data structure usage
  (for-each
    (lambda (feature)
      (when (eq? (feature-type feature) 'function)
        (let ((feature-node (find-node-by-feature hypergraph feature)))
          (when feature-node
            ;; Look for data structures used by this function
            (create-data-usage-edges! hypergraph feature-node features)))))
    features))

;; Cross-system cognitive synergy (blueprint requirement)
(define (compose-hybrid-agent components)
  "Create composite hypernode representing emergent hybrid capabilities"
  (let ((agent-id (gensym "hybrid-agent-"))
        (attributes `((component-count . ,(length components))
                      (creation-time . ,(current-time))
                      (synergy-type . emergent))))
    (make-hypernode
      agent-id
      'HybridAgent
      components
      attributes
      '())))

;; Create hybrid agents from multiple system components
(define (create-hybrid-agents hypergraph opencog-features elizaos-features gnucash-features)
  "Create hybrid agents combining features from all three systems"
  (let ((hybrid-agents '()))
    
    ;; Account Reasoning Agent (OpenCog PLN + ElizaOS Plugin + GnuCash Ledger)
    (let ((pln-features (filter (lambda (f) 
                                  (string-contains (feature-name f) "pln")) 
                                opencog-features))
          (plugin-features (filter (lambda (f) 
                                     (string-contains (feature-name f) "plugin")) 
                                   elizaos-features))
          (ledger-features (filter (lambda (f) 
                                     (string-contains (feature-name f) "ledger")) 
                                   gnucash-features)))
      (when (and (not (null? pln-features))
                 (not (null? plugin-features))
                 (not (null? ledger-features)))
        (let ((agent (compose-hybrid-agent 
                       (append pln-features plugin-features ledger-features))))
          (set! hybrid-agents (cons agent hybrid-agents))
          (add-hypernode! hypergraph agent))))
    
    ;; Transaction Analysis Agent  
    (let ((reasoning-features (filter (lambda (f) 
                                        (string-contains (feature-name f) "reason")) 
                                      opencog-features))
          (agent-features (filter (lambda (f) 
                                    (string-contains (feature-name f) "agent")) 
                                  elizaos-features))
          (transaction-features (filter (lambda (f) 
                                          (string-contains (feature-name f) "transaction")) 
                                        gnucash-features)))
      (when (and (not (null? reasoning-features))
                 (not (null? agent-features))
                 (not (null? transaction-features)))
        (let ((agent (compose-hybrid-agent 
                       (append reasoning-features agent-features transaction-features))))
          (set! hybrid-agents (cons agent hybrid-agents))
          (add-hypernode! hypergraph agent))))
    
    hybrid-agents))

;; Unified data model creation (blueprint requirement)
(define (hybrid-transaction amount from to category timestamp)
  "Create unified hybrid transaction data structure"
  (let ((trans-id (gensym "hybrid-trans-"))
        (attributes `((amount . ,amount)
                      (from-account . ,from)
                      (to-account . ,to)
                      (category . ,category)
                      (timestamp . ,timestamp)
                      (cognitive-tags . ())
                      (reasoning-metadata . ())
                      (agent-processed . #f))))
    (make-hypernode
      trans-id
      'HybridTransaction
      `((amount . ,amount)
        (from . ,from)
        (to . ,to)
        (category . ,category)
        (timestamp . ,timestamp))
      attributes
      '())))

;; Helper functions

(define (find-node-by-feature hypergraph feature)
  "Find hypernode containing specific feature"
  (hash-fold
    (lambda (id node result)
      (if (and (eq? (hypernode-type node) 'Feature)
               (equal? (hypernode-content node) feature))
          node
          result))
    #f
    (hypergraph-nodes hypergraph)))

(define (find-node-by-name hypergraph name)
  "Find hypernode by feature name"
  (hash-fold
    (lambda (id node result)
      (if (and (eq? (hypernode-type node) 'Feature)
               (equal? (assoc-ref (hypernode-attributes node) 'name) name))
          node
          result))
    #f
    (hypergraph-nodes hypergraph)))

(define (group-features-by-language features)
  "Group features by programming language"
  (let ((language-table (make-hash-table)))
    (for-each
      (lambda (feature)
        (let ((lang (feature-language feature)))
          (hash-set! language-table lang
                     (cons feature (hash-ref language-table lang '())))))
      features)
    (hash-map->list cons language-table)))

(define (create-language-interface-edges! hypergraph features language)
  "Create interface edges between features of the same language"
  (when (> (length features) 1)
    (for-each
      (lambda (f1)
        (for-each
          (lambda (f2)
            (when (not (equal? f1 f2))
              (let ((n1 (find-node-by-feature hypergraph f1))
                    (n2 (find-node-by-feature hypergraph f2)))
                (when (and n1 n2)
                  (let ((edge (link-features n1 n2 'interface-compatible
                                           0.6 `((language . ,language)))))
                    (add-hyperedge! hypergraph edge))))))
          features))
      features)))

(define (create-data-usage-edges! hypergraph feature-node features)
  "Create edges for data structure usage by functions"
  (let ((data-structures (filter (lambda (f) 
                                   (eq? (feature-type f) 'data-structure)) 
                                 features)))
    (for-each
      (lambda (data-struct)
        (let ((struct-node (find-node-by-feature hypergraph data-struct)))
          (when struct-node
            ;; Simple heuristic: if function name contains structure name
            (when (string-contains 
                    (feature-name (hypernode-content feature-node))
                    (feature-name data-struct))
              (let ((edge (link-features feature-node struct-node 'uses-data
                                       0.7 `((usage-type . structure)))))
                (add-hyperedge! hypergraph edge))))))
      data-structures)))

;; Hypergraph analysis and metrics

(define (hypergraph-statistics hypergraph)
  "Generate statistics for hypergraph"
  (let ((node-count (hash-count (const #t) (hypergraph-nodes hypergraph)))
        (edge-count (hash-count (const #t) (hypergraph-edges hypergraph))))
    `((nodes . ,node-count)
      (edges . ,edge-count)
      (density . ,(if (> node-count 1) 
                      (/ edge-count (* node-count (- node-count 1))) 
                      0))
      (node-types . ,(get-node-type-distribution hypergraph))
      (edge-types . ,(get-edge-type-distribution hypergraph)))))

(define (get-node-type-distribution hypergraph)
  "Get distribution of node types"
  (let ((type-counts (make-hash-table)))
    (hash-for-each
      (lambda (id node)
        (let ((type (hypernode-type node)))
          (hash-set! type-counts type
                     (+ 1 (hash-ref type-counts type 0)))))
      (hypergraph-nodes hypergraph))
    (hash-map->list cons type-counts)))

(define (get-edge-type-distribution hypergraph)
  "Get distribution of edge types"
  (let ((type-counts (make-hash-table)))
    (hash-for-each
      (lambda (id edge)
        (let ((type (hyperedge-type edge)))
          (hash-set! type-counts type
                     (+ 1 (hash-ref type-counts type 0)))))
      (hypergraph-edges hypergraph))
    (hash-map->list cons type-counts)))

;; Export main functions
(export create-hypergraph
        feature->hypernode link-features
        add-hypernode! add-hyperedge!
        extract-and-encode-repository
        compose-hybrid-agent create-hybrid-agents
        hybrid-transaction
        hypergraph-statistics
        make-hypernode hypernode? 
        hypernode-id hypernode-type hypernode-content hypernode-attributes
        make-hyperedge hyperedge?
        hyperedge-id hyperedge-type hyperedge-nodes hyperedge-attributes hyperedge-weight)