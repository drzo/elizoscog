;; extract-features.scm
;; Cognitive Integration Blueprint: Feature Extraction
;; Recursively traverses repositories and extracts all functions, classes, and API endpoints

(define-module (hypergraph extract-features))

(use-modules (ice-9 ftw)
             (ice-9 regex) 
             (ice-9 textual-ports)
             (srfi srfi-1)
             (srfi srfi-9))

;; Feature record type
(define-record-type <feature>
  (make-feature name type language file line dependencies metadata)
  feature?
  (name feature-name)
  (type feature-type)          ; 'function, 'class, 'api-endpoint, 'data-structure
  (language feature-language)  ; 'scheme, 'python, 'c, 'cpp, 'javascript
  (file feature-file)
  (line feature-line)
  (dependencies feature-dependencies)
  (metadata feature-metadata))

;; Repository traversal state
(define-record-type <repo-state>
  (make-repo-state path features current-file)
  repo-state?
  (path repo-state-path)
  (features repo-state-features)
  (current-file repo-state-current-file))

;; Main extraction function as specified in the blueprint
(define (extract-features repo-path)
  "Extract all features from repository at repo-path"
  (let ((state (make-repo-state repo-path '() #f)))
    (repo-state-features (traverse-repository state))))

;; File type detection
(define (detect-file-language filename)
  "Detect programming language from file extension"
  (cond
    ((string-suffix? ".scm" filename) 'scheme)
    ((string-suffix? ".py" filename) 'python)
    ((string-suffix? ".c" filename) 'c)
    ((string-suffix? ".cpp" filename) 'cpp)
    ((string-suffix? ".cc" filename) 'cpp)
    ((string-suffix? ".cxx" filename) 'cpp)
    ((string-suffix? ".js" filename) 'javascript)
    ((string-suffix? ".ts" filename) 'typescript)
    ((string-suffix? ".h" filename) 'c-header)
    ((string-suffix? ".hpp" filename) 'cpp-header)
    (else 'unknown)))

;; Repository traversal
(define (traverse-repository state)
  "Recursively traverse repository and extract features"
  (define (visit-file filename stat result)
    (if (regular-file? stat)
        (let ((language (detect-file-language filename)))
          (if (not (eq? language 'unknown))
              (let ((new-features (parse-file filename language)))
                (make-repo-state
                  (repo-state-path state)
                  (append (repo-state-features state) new-features)
                  filename))
              state))
        state))
  
  (define (visit-directory dirname stat result)
    ;; Skip hidden directories and common build/dependency directories
    (not (or (string-prefix? "." (basename dirname))
             (string-suffix? "/.git" dirname)
             (string-suffix? "/node_modules" dirname)
             (string-suffix? "/build" dirname)
             (string-suffix? "/__pycache__" dirname))))
  
  (file-system-fold visit-file visit-directory
                    (lambda (dirname stat errno result) result)
                    state
                    (repo-state-path state)))

;; Language-specific parsing
(define (parse-file filename language)
  "Parse file and extract features based on language"
  (with-exception-handler
    (lambda (exn)
      (format #t "Warning: Failed to parse ~a: ~a~%" filename exn)
      '())
    (lambda ()
      (case language
        ((scheme) (parse-scheme-file filename))
        ((python) (parse-python-file filename))
        ((c cpp) (parse-c-cpp-file filename))
        ((javascript typescript) (parse-js-file filename))
        (else '())))
    #:unwind? #t))

;; Scheme file parsing
(define (parse-scheme-file filename)
  "Extract features from Scheme file"
  (define features '())
  (define line-number 0)
  
  (call-with-input-file filename
    (lambda (port)
      (let loop ((expr (read port)))
        (set! line-number (+ line-number 1))
        (unless (eof-object? expr)
          (when (pair? expr)
            (case (car expr)
              ((define define-public)
               (when (> (length expr) 2)
                 (let ((name (if (pair? (cadr expr))
                               (car (cadr expr))  ; function definition
                               (cadr expr))))      ; variable definition
                   (set! features
                     (cons (make-feature
                             (symbol->string name)
                             (if (pair? (cadr expr)) 'function 'variable)
                             'scheme
                             filename
                             line-number
                             (extract-scheme-dependencies expr)
                             `((definition-type . ,(car expr))
                               (body-size . ,(length (cddr expr)))))
                           features)))))
              ((define-module)
               (when (> (length expr) 1)
                 (set! features
                   (cons (make-feature
                           (symbol->string (cadr expr))
                           'module
                           'scheme
                           filename
                           line-number
                           '()
                           `((module-name . ,(cadr expr))))
                         features))))
              ((define-record-type)
               (when (> (length expr) 1)
                 (set! features
                   (cons (make-feature
                           (symbol->string (cadr expr))
                           'data-structure
                           'scheme
                           filename
                           line-number
                           '()
                           `((record-type . #t)))
                         features))))))
          (loop (read port))))))
  features)

;; Python file parsing (simplified)
(define (parse-python-file filename)
  "Extract features from Python file"
  (define features '())
  (define line-number 0)
  
  (call-with-input-file filename
    (lambda (port)
      (let loop ((line (get-line port)))
        (set! line-number (+ line-number 1))
        (unless (eof-object? line)
          ;; Extract function definitions
          (when (string-match "^[[:space:]]*def[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)
            (let ((match (string-match "^[[:space:]]*def[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)))
              (when match
                (set! features
                  (cons (make-feature
                          (match:substring match 1)
                          'function
                          'python
                          filename
                          line-number
                          (extract-python-dependencies line)
                          `((async . ,(string-contains line "async"))))
                        features)))))
          ;; Extract class definitions
          (when (string-match "^[[:space:]]*class[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)
            (let ((match (string-match "^[[:space:]]*class[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)))
              (when match
                (set! features
                  (cons (make-feature
                          (match:substring match 1)
                          'class
                          'python
                          filename
                          line-number
                          '()
                          `((inheritance . ,(string-contains line ":"))))
                        features)))))
          (loop (get-line port))))))
  features)

;; C/C++ file parsing (simplified)
(define (parse-c-cpp-file filename)
  "Extract features from C/C++ file"
  (define features '())
  (define line-number 0)
  
  (call-with-input-file filename
    (lambda (port)
      (let loop ((line (get-line port)))
        (set! line-number (+ line-number 1))
        (unless (eof-object? line)
          ;; Extract function definitions (simplified pattern)
          (when (string-match "^[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)[[:space:]]*\\(" line)
            (let ((match (string-match "^[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)[[:space:]]*\\(" line)))
              (when match
                (set! features
                  (cons (make-feature
                          (match:substring match 1)
                          'function
                          (if (string-suffix? ".cpp" filename) 'cpp 'c)
                          filename
                          line-number
                          '()
                          `((static . ,(string-contains line "static"))
                            (inline . ,(string-contains line "inline"))))
                        features)))))
          ;; Extract struct/class definitions
          (when (string-match "^[[:space:]]*(struct|class)[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)
            (let ((match (string-match "^[[:space:]]*(struct|class)[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)))
              (when match
                (set! features
                  (cons (make-feature
                          (match:substring match 2)
                          'data-structure
                          (if (string-suffix? ".cpp" filename) 'cpp 'c)
                          filename
                          line-number
                          '()
                          `((type . ,(string->symbol (match:substring match 1)))))
                        features)))))
          (loop (get-line port))))))
  features)

;; JavaScript/TypeScript file parsing (simplified)
(define (parse-js-file filename)
  "Extract features from JavaScript/TypeScript file"
  (define features '())
  (define line-number 0)
  
  (call-with-input-file filename
    (lambda (port)
      (let loop ((line (get-line port)))
        (set! line-number (+ line-number 1))
        (unless (eof-object? line)
          ;; Extract function definitions
          (when (string-match "^[[:space:]]*function[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)
            (let ((match (string-match "^[[:space:]]*function[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)))
              (when match
                (set! features
                  (cons (make-feature
                          (match:substring match 1)
                          'function
                          'javascript
                          filename
                          line-number
                          '()
                          `((async . ,(string-contains line "async"))))
                        features)))))
          ;; Extract class definitions
          (when (string-match "^[[:space:]]*class[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)
            (let ((match (string-match "^[[:space:]]*class[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)" line)))
              (when match
                (set! features
                  (cons (make-feature
                          (match:substring match 1)
                          'class
                          'javascript
                          filename
                          line-number
                          '()
                          `((extends . ,(string-contains line "extends"))))
                        features)))))
          (loop (get-line port))))))
  features)

;; Dependency extraction helpers
(define (extract-scheme-dependencies expr)
  "Extract dependencies from Scheme expression"
  ;; Simplified: look for use-modules and other imports
  (cond
    ((and (pair? expr) (eq? (car expr) 'use-modules))
     (map (lambda (mod) (symbol->string mod)) (cdr expr)))
    (else '())))

(define (extract-python-dependencies line)
  "Extract dependencies from Python line"
  ;; Simplified: look for import statements
  (if (string-match "import[[:space:]]+([a-zA-Z_][a-zA-Z0-9_.]*)" line)
      (let ((match (string-match "import[[:space:]]+([a-zA-Z_][a-zA-Z0-9_.]*)" line)))
        (if match (list (match:substring match 1)) '()))
      '()))

;; Feature filtering and analysis
(define (filter-features features predicate)
  "Filter features based on predicate"
  (filter predicate features))

(define (features-by-language features language)
  "Get all features of a specific language"
  (filter (lambda (f) (eq? (feature-language f) language)) features))

(define (features-by-type features type)
  "Get all features of a specific type"
  (filter (lambda (f) (eq? (feature-type f) type)) features))

;; Summary and statistics
(define (feature-summary features)
  "Generate summary statistics for extracted features"
  (let ((languages (delete-duplicates (map feature-language features)))
        (types (delete-duplicates (map feature-type features))))
    `((total-features . ,(length features))
      (languages . ,languages)
      (types . ,types)
      (by-language . ,(map (lambda (lang) 
                             (cons lang (length (features-by-language features lang))))
                           languages))
      (by-type . ,(map (lambda (type)
                         (cons type (length (features-by-type features type))))
                       types)))))

;; Export main functions
(export extract-features
        make-feature feature?
        feature-name feature-type feature-language feature-file feature-line
        feature-dependencies feature-metadata
        filter-features features-by-language features-by-type
        feature-summary)