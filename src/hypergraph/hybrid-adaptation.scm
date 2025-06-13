;; hybrid-adaptation.scm
;; Cognitive Integration Blueprint: Direct Code Synthesis
;; Adapt functions for direct operation in hybrid system without external dependencies

(define-module (hypergraph hybrid-adaptation))

(use-modules (ice-9 match)
             (ice-9 regex)
             (ice-9 textual-ports)
             (ice-9 pretty-print)
             (srfi srfi-1)
             (srfi srfi-9)
             (srfi srfi-26)
             (hypergraph extract-features)
             (hypergraph hypergraph-encoding))

;; Adaptation context record
(define-record-type <adaptation-context>
  (make-adaptation-context hybrid-api target-language mappings transformations)
  adaptation-context?
  (hybrid-api adaptation-context-hybrid-api)           ; Unified hybrid API
  (target-language adaptation-context-target-language) ; Target language for adaptation
  (mappings adaptation-context-mappings)               ; External -> internal mappings
  (transformations adaptation-context-transformations)) ; Code transformation rules

;; Adaptation result record
(define-record-type <adaptation-result>
  (make-adaptation-result original-feature adapted-code dependencies metadata)
  adaptation-result?
  (original-feature adaptation-result-original-feature)
  (adapted-code adaptation-result-adapted-code)
  (dependencies adaptation-result-dependencies)
  (metadata adaptation-result-metadata))

;; Main adaptation function (blueprint requirement)
(define (adapt-function fn hybrid-api)
  "Refactor and adapt function source code for hybrid system operation"
  (let ((context (make-adaptation-context
                   hybrid-api
                   (feature-language fn)
                   (create-default-mappings hybrid-api)
                   (create-default-transformations))))
    (adapt-feature-with-context fn context)))

;; Adapt feature with full context
(define (adapt-feature-with-context feature context)
  "Adapt feature using provided adaptation context"
  (case (feature-language feature)
    ((scheme) (adapt-scheme-feature feature context))
    ((python) (adapt-python-feature feature context))
    ((c cpp) (adapt-c-cpp-feature feature context))
    ((javascript) (adapt-javascript-feature feature context))
    (else (create-fallback-adaptation feature context))))

;; Scheme feature adaptation
(define (adapt-scheme-feature feature context)
  "Adapt Scheme feature for hybrid operation"
  (let* ((source-code (read-feature-source feature))
         (adapted-code (transform-scheme-code source-code context))
         (new-dependencies (extract-hybrid-dependencies adapted-code context)))
    (make-adaptation-result
      feature
      adapted-code
      new-dependencies
      `((adaptation-type . scheme-to-hybrid)
        (original-dependencies . ,(feature-dependencies feature))
        (transformation-count . ,(length (adaptation-context-transformations context)))))))

;; Python feature adaptation
(define (adapt-python-feature feature context)
  "Adapt Python feature for hybrid operation"
  (let* ((source-lines (read-feature-source-lines feature))
         (adapted-lines (map (lambda (line) 
                               (transform-python-line line context)) 
                             source-lines))
         (adapted-code (string-join adapted-lines "\n"))
         (new-dependencies (extract-hybrid-dependencies adapted-code context)))
    (make-adaptation-result
      feature
      adapted-code
      new-dependencies
      `((adaptation-type . python-to-hybrid)
        (line-count . ,(length source-lines))))))

;; C/C++ feature adaptation
(define (adapt-c-cpp-feature feature context)
  "Adapt C/C++ feature for hybrid operation"
  (let* ((source-code (read-feature-source feature))
         (preprocessed-code (preprocess-c-code source-code))
         (adapted-code (transform-c-code preprocessed-code context))
         (new-dependencies (extract-hybrid-dependencies adapted-code context)))
    (make-adaptation-result
      feature
      adapted-code
      new-dependencies
      `((adaptation-type . c-to-hybrid)
        (preprocessing . #t)))))

;; JavaScript feature adaptation
(define (adapt-javascript-feature feature context)
  "Adapt JavaScript feature for hybrid operation"
  (let* ((source-code (read-feature-source feature))
         (adapted-code (transform-javascript-code source-code context))
         (new-dependencies (extract-hybrid-dependencies adapted-code context)))
    (make-adaptation-result
      feature
      adapted-code
      new-dependencies
      `((adaptation-type . js-to-hybrid)
        (async-support . #t)))))

;; Source code reading utilities
(define (read-feature-source feature)
  "Read source code for feature from its file"
  (call-with-input-file (feature-file feature)
    (lambda (port)
      ;; For now, read entire file - in production would extract specific function
      (get-string-all port))))

(define (read-feature-source-lines feature)
  "Read source code lines for feature"
  (call-with-input-file (feature-file feature)
    (lambda (port)
      (let loop ((lines '())
                 (line (get-line port)))
        (if (eof-object? line)
            (reverse lines)
            (loop (cons line lines) (get-line port)))))))

;; Code transformation engines

;; Scheme code transformation
(define (transform-scheme-code source context)
  "Transform Scheme code for hybrid operation"
  (let ((hybrid-api (adaptation-context-hybrid-api context))
        (mappings (adaptation-context-mappings context)))
    ;; Replace external calls with hybrid API calls
    (fold
      (lambda (mapping source-acc)
        (let ((external-call (car mapping))
              (hybrid-call (cdr mapping)))
          (regexp-substitute/global #f external-call source-acc 'pre hybrid-call 'post)))
      source
      mappings)))

;; Python code transformation
(define (transform-python-line line context)
  "Transform single Python line for hybrid operation"
  (let ((mappings (adaptation-context-mappings context)))
    (fold
      (lambda (mapping line-acc)
        (let ((external-pattern (car mapping))
              (hybrid-replacement (cdr mapping)))
          (regexp-substitute/global #f external-pattern line-acc 'pre hybrid-replacement 'post)))
      line
      mappings)))

;; C/C++ code transformation
(define (preprocess-c-code source)
  "Preprocess C/C++ code before transformation"
  ;; Remove preprocessor directives that reference external libraries
  (regexp-substitute/global #f "#include\\s+<[^>]+>" source 'pre "" 'post))

(define (transform-c-code source context)
  "Transform C/C++ code for hybrid operation"
  (let ((mappings (adaptation-context-mappings context)))
    (fold
      (lambda (mapping source-acc)
        (let ((external-call (car mapping))
              (hybrid-call (cdr mapping)))
          (regexp-substitute/global #f external-call source-acc 'pre hybrid-call 'post)))
      source
      mappings)))

;; JavaScript code transformation
(define (transform-javascript-code source context)
  "Transform JavaScript code for hybrid operation"
  (let ((mappings (adaptation-context-mappings context)))
    ;; Transform require/import statements
    (let ((transformed (regexp-substitute/global #f 
                          "require\\(['\"]([^'\"]+)['\"]\\)" 
                          source 
                          'pre "hybrid_require('\\1')" 'post)))
      ;; Apply other mappings
      (fold
        (lambda (mapping source-acc)
          (let ((external-pattern (car mapping))
                (hybrid-replacement (cdr mapping)))
            (regexp-substitute/global #f external-pattern source-acc 'pre hybrid-replacement 'post)))
        transformed
        mappings))))

;; Mapping creation utilities
(define (create-default-mappings hybrid-api)
  "Create default external->hybrid mappings"
  (list
    ;; OpenCog mappings
    (cons "atomspace\\." "hybrid_api.atomspace.")
    (cons "cogserver\\." "hybrid_api.cogserver.")
    (cons "pln\\." "hybrid_api.reasoning.")
    
    ;; ElizaOS mappings  
    (cons "elizaos\\." "hybrid_api.agents.")
    (cons "agent\\." "hybrid_api.agents.")
    (cons "plugin\\." "hybrid_api.plugins.")
    
    ;; GnuCash mappings
    (cons "gnucash\\." "hybrid_api.financial.")
    (cons "libgnucash\\." "hybrid_api.financial.core.")
    (cons "qof\\." "hybrid_api.financial.qof.")
    
    ;; Database mappings
    (cons "sqlite3\\." "hybrid_api.storage.")
    (cons "postgresql\\." "hybrid_api.storage.")
    (cons "mysql\\." "hybrid_api.storage.")
    
    ;; Network mappings
    (cons "http\\." "hybrid_api.network.")
    (cons "requests\\." "hybrid_api.network.requests.")
    (cons "urllib\\." "hybrid_api.network.urllib.")))

;; Transformation rule creation
(define (create-default-transformations)
  "Create default code transformation rules"
  (list
    ;; Asynchronous function patterns
    `(async-function . ,(lambda (code) 
                          (regexp-substitute/global #f 
                            "def\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(" 
                            code 
                            'pre "async def \\1(" 'post)))
    
    ;; Error handling patterns
    `(error-handling . ,(lambda (code)
                          (string-append
                            "try:\n"
                            "    " (regexp-substitute/global #f "\n" code 'pre "\n    " 'post)
                            "\nexcept Exception as e:\n"
                            "    hybrid_api.log_error(e)\n"
                            "    raise")))
    
    ;; Logging injection
    `(logging . ,(lambda (code)
                   (string-append
                     "hybrid_api.log_function_entry('" (gensym) "')\n"
                     code
                     "\nhybrid_api.log_function_exit('" (gensym) "')")))))

;; Dependency analysis for adapted code
(define (extract-hybrid-dependencies code context)
  "Extract dependencies from adapted code"
  (let ((dependencies '()))
    ;; Look for hybrid_api calls
    (when (string-contains code "hybrid_api.")
      (set! dependencies (cons "hybrid-api-core" dependencies)))
    
    ;; Look for async patterns
    (when (string-contains code "async")
      (set! dependencies (cons "async-runtime" dependencies)))
    
    ;; Look for storage calls
    (when (string-contains code "hybrid_api.storage")
      (set! dependencies (cons "hybrid-storage" dependencies)))
    
    ;; Look for network calls
    (when (string-contains code "hybrid_api.network")
      (set! dependencies (cons "hybrid-network" dependencies)))
    
    (delete-duplicates dependencies)))

;; Batch adaptation for multiple features
(define (adapt-features features hybrid-api)
  "Adapt multiple features for hybrid operation"
  (map (lambda (feature) (adapt-function feature hybrid-api)) features))

;; Repository-wide adaptation
(define (adapt-repository repo-path hybrid-api output-path)
  "Adapt entire repository for hybrid operation"
  (let* ((features (extract-features repo-path))
         (context (make-adaptation-context
                    hybrid-api
                    'multi-language
                    (create-default-mappings hybrid-api)
                    (create-default-transformations)))
         (adaptations (map (lambda (f) (adapt-feature-with-context f context)) features)))
    
    ;; Write adapted code to output directory
    (create-adapted-repository output-path adaptations)
    
    ;; Return adaptation summary
    `((total-features . ,(length features))
      (adapted-features . ,(length adaptations))
      (output-path . ,output-path)
      (languages . ,(delete-duplicates (map feature-language features)))
      (adaptation-metadata . ,(map adaptation-result-metadata adaptations)))))

;; Output generation
(define (create-adapted-repository output-path adaptations)
  "Create repository structure with adapted code"
  (unless (file-exists? output-path)
    (mkdir output-path))
  
  ;; Create language-specific directories
  (let ((languages (delete-duplicates 
                     (map (lambda (a) 
                            (feature-language (adaptation-result-original-feature a))) 
                          adaptations))))
    (for-each
      (lambda (lang)
        (let ((lang-dir (string-append output-path "/" (symbol->string lang))))
          (unless (file-exists? lang-dir)
            (mkdir lang-dir))))
      languages))
  
  ;; Write adapted code files
  (for-each
    (lambda (adaptation)
      (let* ((feature (adaptation-result-original-feature adaptation))
             (lang (feature-language feature))
             (filename (string-append output-path "/" 
                                    (symbol->string lang) "/"
                                    "adapted-" (feature-name feature) 
                                    (get-file-extension lang))))
        (call-with-output-file filename
          (lambda (port)
            (display (adaptation-result-adapted-code adaptation) port)))))
    adaptations))

;; Utility functions
(define (get-file-extension language)
  "Get file extension for language"
  (case language
    ((scheme) ".scm")
    ((python) ".py")
    ((c) ".c")
    ((cpp) ".cpp")
    ((javascript) ".js")
    (else ".txt")))

(define (create-fallback-adaptation feature context)
  "Create fallback adaptation for unsupported languages"
  (make-adaptation-result
    feature
    (string-append ";; Fallback adaptation for " (feature-name feature) "\n"
                   ";; Original language: " (symbol->string (feature-language feature)) "\n"
                   ";; TODO: Implement adaptation for this language\n")
    '()
    `((adaptation-type . fallback)
      (requires-manual-adaptation . #t))))

;; Integration with hypergraph encoding
(define (adapt-and-encode-features features hybrid-api)
  "Adapt features and encode them in hypergraph"
  (let ((hypergraph (create-hypergraph))
        (adaptations (adapt-features features hybrid-api)))
    
    ;; Create hypernodes for original and adapted features
    (for-each
      (lambda (adaptation)
        (let* ((original-feature (adaptation-result-original-feature adaptation))
               (original-node (feature->hypernode original-feature 
                                                 `((status . original))))
               (adapted-node (make-hypernode
                              (gensym "adapted-")
                              'AdaptedFeature
                              (adaptation-result-adapted-code adaptation)
                              `((adaptation-metadata . ,(adaptation-result-metadata adaptation))
                                (new-dependencies . ,(adaptation-result-dependencies adaptation)))
                              '())))
          (add-hypernode! hypergraph original-node)
          (add-hypernode! hypergraph adapted-node)
          
          ;; Link original to adapted
          (let ((adaptation-edge (link-features original-node adapted-node 'adapted-to
                                              1.0 `((adaptation-type . hybrid)))))
            (add-hyperedge! hypergraph adaptation-edge))))
      adaptations)
    
    (values hypergraph adaptations)))

;; Export main functions
(export adapt-function adapt-features adapt-repository
        adapt-and-encode-features
        make-adaptation-context adaptation-context?
        make-adaptation-result adaptation-result?
        adaptation-result-original-feature adaptation-result-adapted-code
        adaptation-result-dependencies adaptation-result-metadata
        create-default-mappings create-default-transformations)