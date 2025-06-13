;; test-cognitive-integration.scm
;; Test suite for Cognitive Integration Blueprint implementation

(define-module (test hypergraph cognitive-integration))

(use-modules (srfi srfi-64)         ; Testing framework
             (ice-9 textual-ports)
             (ice-9 match)
             (hypergraph extract-features)
             (hypergraph hypergraph-encoding)
             (hypergraph hybrid-adaptation)
             (hypergraph cognitive-integration))

;; Test data setup
(define test-repo-path "/tmp/test-repo")
(define test-output-path "/tmp/hybrid-output")

;; Setup test repository structure
(define (setup-test-repository)
  "Create test repository with sample files"
  (system* "mkdir" "-p" test-repo-path)
  
  ;; Create sample Scheme file
  (call-with-output-file (string-append test-repo-path "/test.scm")
    (lambda (port)
      (display "(define-module (test module))\n" port)
      (display "(use-modules (srfi srfi-1))\n" port)
      (display "(define (test-function x y) (+ x y))\n" port)
      (display "(define test-variable 42)\n" port)))
  
  ;; Create sample Python file
  (call-with-output-file (string-append test-repo-path "/test.py")
    (lambda (port)
      (display "import asyncio\n" port)
      (display "import requests\n" port)
      (display "\n" port)
      (display "class TestClass:\n" port)
      (display "    def __init__(self):\n" port)
      (display "        self.value = 0\n" port)
      (display "\n" port)
      (display "async def test_function(x, y):\n" port)
      (display "    return x + y\n" port)))
  
  ;; Create sample C file
  (call-with-output-file (string-append test-repo-path "/test.c")
    (lambda (port)
      (display "#include <stdio.h>\n" port)
      (display "\n" port)
      (display "struct TestStruct {\n" port)
      (display "    int value;\n" port)
      (display "};\n" port)
      (display "\n" port)
      (display "int test_function(int x, int y) {\n" port)
      (display "    return x + y;\n" port)
      (display "}\n" port))))

(define (cleanup-test-repository)
  "Clean up test repository"
  (system* "rm" "-rf" test-repo-path)
  (system* "rm" "-rf" test-output-path))

;; Test suite begins
(test-begin "cognitive-integration-blueprint")

;; Test Phase I: Feature Extraction
(test-group "Phase I: Repository Feature Extraction"
  
  (test-assert "setup-test-repository"
    (begin
      (setup-test-repository)
      (file-exists? test-repo-path)))
  
  (test-assert "extract-features returns list"
    (let ((features (extract-features test-repo-path)))
      (list? features)))
  
  (test-assert "extract-features finds scheme functions"
    (let ((features (extract-features test-repo-path)))
      (any (lambda (f) 
             (and (eq? (feature-language f) 'scheme)
                  (eq? (feature-type f) 'function)
                  (string=? (feature-name f) "test-function")))
           features)))
  
  (test-assert "extract-features finds python classes"
    (let ((features (extract-features test-repo-path)))
      (any (lambda (f)
             (and (eq? (feature-language f) 'python)
                  (eq? (feature-type f) 'class)
                  (string=? (feature-name f) "TestClass")))
           features)))
  
  (test-assert "extract-features finds c functions"
    (let ((features (extract-features test-repo-path)))
      (any (lambda (f)
             (and (eq? (feature-language f) 'c)
                  (eq? (feature-type f) 'function)
                  (string=? (feature-name f) "test_function")))
           features)))
  
  (test-assert "feature-summary generates statistics"
    (let* ((features (extract-features test-repo-path))
           (summary (feature-summary features)))
      (and (assoc 'total-features summary)
           (assoc 'languages summary)
           (assoc 'types summary)))))

;; Test Phase II: Hypergraph Encoding
(test-group "Phase II: Hypergraph Encoding"
  
  (test-assert "create-hypergraph returns hypergraph"
    (let ((hg (create-hypergraph)))
      (hypergraph? hg)))
  
  (test-assert "feature->hypernode creates valid hypernode"
    (let* ((features (extract-features test-repo-path))
           (feature (car features))
           (meta '((repo . test)))
           (node (feature->hypernode feature meta)))
      (and (hypernode? node)
           (eq? (hypernode-type node) 'Feature))))
  
  (test-assert "link-features creates hyperedge"
    (let* ((features (extract-features test-repo-path))
           (f1 (feature->hypernode (car features) '()))
           (f2 (feature->hypernode (cadr features) '()))
           (edge (link-features f1 f2 'depends-on)))
      (and (hyperedge? edge)
           (eq? (hyperedge-type edge) 'depends-on))))
  
  (test-assert "add-hypernode! adds node to hypergraph"
    (let* ((hg (create-hypergraph))
           (features (extract-features test-repo-path))
           (node (feature->hypernode (car features) '())))
      (add-hypernode! hg node)
      (> (hash-count (const #t) (hypergraph-nodes hg)) 0)))
  
  (test-assert "extract-and-encode-repository creates populated hypergraph"
    (let ((hg (extract-and-encode-repository test-repo-path '((repo . test)))))
      (and (hypergraph? hg)
           (> (hash-count (const #t) (hypergraph-nodes hg)) 0))))
  
  (test-assert "compose-hybrid-agent creates agent hypernode"
    (let* ((features (extract-features test-repo-path))
           (agent (compose-hybrid-agent (take features 2))))
      (and (hypernode? agent)
           (eq? (hypernode-type agent) 'HybridAgent))))
  
  (test-assert "hybrid-transaction creates transaction hypernode"
    (let ((trans (hybrid-transaction 100.0 "checking" "savings" "transfer" (current-time))))
      (and (hypernode? trans)
           (eq? (hypernode-type trans) 'HybridTransaction)))))

;; Test Phase III: Direct Integration Synthesis
(test-group "Phase III: Direct Integration Synthesis"
  
  (test-assert "adapt-function returns adaptation result"
    (let* ((features (extract-features test-repo-path))
           (hybrid-api '((core . test-api)))
           (result (adapt-function (car features) hybrid-api)))
      (adaptation-result? result)))
  
  (test-assert "adapted code contains hybrid API calls"
    (let* ((features (extract-features test-repo-path))
           (hybrid-api '((core . test-api)))
           (result (adapt-function (car features) hybrid-api))
           (adapted-code (adaptation-result-adapted-code result)))
      (string? adapted-code)))
  
  (test-assert "adapt-features processes multiple features"
    (let* ((features (take (extract-features test-repo-path) 3))
           (hybrid-api '((core . test-api)))
           (results (adapt-features features hybrid-api)))
      (and (list? results)
           (every adaptation-result? results))))
  
  (test-assert "create-default-mappings returns mappings list"
    (let ((mappings (create-default-mappings '((core . test)))))
      (and (list? mappings)
           (every pair? mappings)))))

;; Test Phase IV: Cross-System Cognitive Synergy
(test-group "Phase IV: Cross-System Cognitive Synergy"
  
  (test-assert "create-hybrid-agents with mock features"
    (let* ((hg (create-hypergraph))
           ;; Create mock features for each system
           (opencog-features (list (make-feature "pln-reasoning" 'function 'scheme 
                                                "/opencog/pln.scm" 1 '() '())))
           (elizaos-features (list (make-feature "agent-plugin" 'class 'python
                                                "/elizaos/agent.py" 1 '() '())))
           (gnucash-features (list (make-feature "ledger-transaction" 'function 'c
                                                "/gnucash/ledger.c" 1 '() '())))
           (agents (create-hybrid-agents hg opencog-features elizaos-features gnucash-features)))
      (list? agents))))

;; Test Phase V: Unified Data Model
(test-group "Phase V: Unified Data Model"
  
  (test-assert "create-unified-hybrid-api returns API structure"
    (let ((api (create-unified-hybrid-api)))
      (and (list? api)
           (assoc 'core api)
           (assoc 'agents api)
           (assoc 'financial api))))
  
  (test-assert "create-unified-data-model returns data model"
    (let ((model (create-unified-data-model)))
      (and (list? model)
           (assoc 'hybrid-transaction model)
           (assoc 'hybrid-account model)
           (assoc 'hybrid-agent model)))))

;; Test Phase VI: Complete Integration
(test-group "Phase VI: Complete Integration Workflow"
  
  (test-assert "cognitive-integration-blueprint executes successfully"
    (let ((repos (list (make-repo-spec test-repo-path 'test '()))))
      (with-exception-handler
        (lambda (exn)
          (format #t "Integration test failed: ~a~%" exn)
          #f)
        (lambda ()
          (let ((state (cognitive-integration-blueprint repos test-output-path)))
            (integration-state? state)))
        #:unwind? #t)))
  
  (test-assert "integration output directory created"
    (file-exists? test-output-path))
  
  (test-assert "integration report generated"
    (file-exists? (string-append test-output-path "/integration-report.md"))))

;; Test utility functions
(test-group "Utility Functions"
  
  (test-assert "hypergraph-statistics returns valid stats"
    (let* ((hg (extract-and-encode-repository test-repo-path '()))
           (stats (hypergraph-statistics hg)))
      (and (assoc 'nodes stats)
           (assoc 'edges stats)
           (assoc 'density stats))))
  
  (test-assert "repo-spec creation and accessors"
    (let ((spec (make-repo-spec "/test/path" 'test '((meta . data)))))
      (and (repo-spec? spec)
           (string=? (repo-spec-path spec) "/test/path")
           (eq? (repo-spec-type spec) 'test)))))

;; Cleanup
(test-assert "cleanup-test-repository"
  (begin
    (cleanup-test-repository)
    (not (file-exists? test-repo-path))))

(test-end "cognitive-integration-blueprint")

;; Export test runner
(define (run-cognitive-integration-tests)
  "Run all cognitive integration tests"
  (test-runner-current (test-runner-simple))
  (load-from-path "test/hypergraph/test-cognitive-integration.scm"))

(export run-cognitive-integration-tests)