;; attention OpenCog Integration with ECAN Activation Spreading
;; Description: OpenCog Attention Allocation Subsystem with ECAN
;; Original Repository: https://github.com/opencog/attention
;; Enhanced: 2025-07-13 with ECAN algorithms

(use-modules (opencog)
             (opencog atom-types)
             (opencog exec)
             (opencog query)
             (opencog rule-engine)
             (srfi srfi-1)
             (ice-9 threads))

;; ECAN attention value predicates
(define attention-importance-predicate (PredicateNode "attention:importance"))
(define attention-urgency-predicate (PredicateNode "attention:urgency"))
(define attention-sti-predicate (PredicateNode "attention:sti"))
(define attention-lti-predicate (PredicateNode "attention:lti"))
(define attention-rent-predicate (PredicateNode "attention:rent"))

;; ECAN attention bank
(define attention-bank-node (ConceptNode "attention:Bank"))
(define attention-bank-funds 1000.0)

;; Define attention atom types with ECAN values
(define (create-attention-atom name importance urgency sti lti)
  "Create an atom with ECAN attention values"
  (let ((atom (ConceptNode (string-append "attention:" name))))
    ;; Set ECAN attention values
    (cog-set-tv! 
      (EvaluationLink attention-importance-predicate (ListLink atom (NumberNode importance)))
      (stv 0.9 0.9))
    (cog-set-tv!
      (EvaluationLink attention-urgency-predicate (ListLink atom (NumberNode urgency)))
      (stv 0.9 0.9))
    (cog-set-tv!
      (EvaluationLink attention-sti-predicate (ListLink atom (NumberNode sti)))
      (stv 0.9 0.9))
    (cog-set-tv!
      (EvaluationLink attention-lti-predicate (ListLink atom (NumberNode lti)))
      (stv 0.9 0.9))
    atom))

;; ECAN activation spreading mechanism
(define (spread-activation source-atom activation-amount max-spread-distance)
  "Implement ECAN-style activation spreading"
  (define (get-connected-atoms atom distance)
    "Get atoms connected to the source atom within distance"
    (if (> distance max-spread-distance)
        '()
        (let ((direct-connections 
               (filter (lambda (link)
                        (and (cog-link? link)
                             (member atom (cog-outgoing-set link))))
                       (cog-get-all-nodes))))
          ;; Recursively get connections
          (append direct-connections
                  (append-map (lambda (connected)
                               (if (not (equal? connected atom))
                                   (get-connected-atoms connected (+ distance 1))
                                   '()))
                             direct-connections)))))
  
  (let ((connected-atoms (get-connected-atoms source-atom 0)))
    (for-each (lambda (target-atom)
               (when (not (equal? target-atom source-atom))
                 (let* ((distance (calculate-atom-distance source-atom target-atom))
                        (spread-factor (/ 1.0 (+ distance 1)))
                        (spread-amount (* activation-amount spread-factor)))
                   (update-sti-value target-atom spread-amount))))
             connected-atoms)))

;; Helper function to calculate distance between atoms
(define (calculate-atom-distance atom1 atom2)
  "Calculate semantic distance between two atoms (simplified)"
  ;; In a real implementation, this would use proper graph distance
  1)

;; Update STI (Short Term Importance) value
(define (update-sti-value atom sti-change)
  "Update the STI value of an atom"
  (let* ((current-sti-link (car (cog-filter 
                                 (lambda (link)
                                   (and (equal? (cog-type link) 'EvaluationLink)
                                        (equal? (gar link) attention-sti-predicate)
                                        (member atom (cog-outgoing-set (gdr link)))))
                                 (cog-incoming-set atom))))
         (current-sti (if current-sti-link
                         (string->number (cog-name (cadadr (cog-outgoing-set current-sti-link))))
                         0.0))
         (new-sti (+ current-sti sti-change)))
    (cog-set-tv!
      (EvaluationLink attention-sti-predicate (ListLink atom (NumberNode new-sti)))
      (stv 0.9 0.9))))

;; ECAN rent collection mechanism  
(define (collect-attention-rent)
  "Implement ECAN rent collection from atoms"
  (let ((all-attention-atoms (cog-filter 
                              (lambda (atom)
                                (string-prefix? "attention:" (cog-name atom)))
                              (cog-get-all-nodes))))
    (let ((total-rent 0.0))
      (for-each (lambda (atom)
                 (let* ((importance (get-attention-value atom 'importance))
                        (sti (get-attention-value atom 'sti))
                        (rent (* importance 0.1))  ; 10% rent rate
                        (new-sti (max 0.0 (- sti rent))))
                   (update-sti-value atom (- rent))
                   (set! total-rent (+ total-rent rent))))
               all-attention-atoms)
      (set! attention-bank-funds (+ attention-bank-funds total-rent))
      (display (string-append "Collected rent: " (number->string total-rent) "\n"))
      total-rent)))

;; Get attention value for an atom
(define (get-attention-value atom value-type)
  "Get a specific attention value (importance, urgency, sti, lti) for an atom"
  (let ((predicate (case value-type
                    ((importance) attention-importance-predicate)
                    ((urgency) attention-urgency-predicate)
                    ((sti) attention-sti-predicate)
                    ((lti) attention-lti-predicate)
                    (else #f))))
    (if predicate
        (let ((links (cog-filter 
                      (lambda (link)
                        (and (equal? (cog-type link) 'EvaluationLink)
                             (equal? (gar link) predicate)
                             (member atom (cog-outgoing-set (gdr link)))))
                      (cog-incoming-set atom))))
          (if (not (null? links))
              (string->number (cog-name (cadadr (cog-outgoing-set (car links)))))
              0.0))
        0.0)))

;; ECAN economic scheduling
(define (schedule-attention-resources agent-requests)
  "Schedule agents based on ECAN economic attention values"
  (let ((agents-with-importance 
         (map (lambda (request)
               (let* ((agent-id (assoc-ref request 'agent-id))
                      (atom (ConceptNode (string-append "attention:" agent-id)))
                      (importance (get-attention-value atom 'importance))
                      (urgency (get-attention-value atom 'urgency))
                      (sti (get-attention-value atom 'sti))
                      (total-importance (+ importance (* urgency 0.5) sti)))
                 (cons request total-importance)))
             agent-requests)))
    ;; Sort by importance (highest first)
    (let ((sorted-agents (sort agents-with-importance 
                              (lambda (a b) (> (cdr a) (cdr b))))))
      ;; Return allocation plan
      (map (lambda (agent-pair index)
            (let* ((request (car agent-pair))
                   (importance (cdr agent-pair))
                   (agent-id (assoc-ref request 'agent-id))
                   (resource-percentage (/ 1.0 (+ index 1))))  ; Simple allocation
              (list agent-id importance resource-percentage)))
          sorted-agents (iota (length sorted-agents))))))

;; Real-time attention monitoring
(define attention-monitoring-active #f)

(define (start-attention-monitoring)
  "Start real-time ECAN attention monitoring"
  (set! attention-monitoring-active #t)
  (call-with-new-thread
   (lambda ()
     (while attention-monitoring-active
       (collect-attention-rent)
       (let ((active-atoms (length (cog-filter 
                                    (lambda (atom)
                                      (string-prefix? "attention:" (cog-name atom)))
                                    (cog-get-all-nodes)))))
         (display (string-append "Active attention atoms: " 
                                (number->string active-atoms) 
                                ", Bank funds: " 
                                (number->string attention-bank-funds) "\n")))
       (sleep 5))))  ; Monitor every 5 seconds
  (display "ECAN attention monitoring started\n"))

(define (stop-attention-monitoring)
  "Stop real-time attention monitoring"
  (set! attention-monitoring-active #f)
  (display "ECAN attention monitoring stopped\n"))

;; Enhanced attention initialization function
(define (initialize-attention)
  "Initialize attention integration with ECAN capabilities"
  (let ((init-link (EvaluationLink
                     (attention-predicate-node "initialized")
                     attention-knowledge-base)))
    (cog-set-tv! init-link (stv 0.9 0.9))
    
    ;; Initialize attention bank
    (cog-set-tv!
      (EvaluationLink (PredicateNode "attention:bank-funds")
                     (ListLink attention-bank-node (NumberNode attention-bank-funds)))
      (stv 0.9 0.9))
    
    ;; Start monitoring
    (start-attention-monitoring)
    
    (display "Initialized ECAN attention integration\n")
    init-link))

;; attention query function
(define (query-attention pattern)
  "Execute query against attention knowledge"
  (let ((query-link (GetLink pattern)))
    (cog-execute! query-link)))

;; attention reasoning rules
(define attention-rule
  (BindLink
    (VariableList
      (VariableNode "$A")
      (VariableNode "$B"))
    (AndLink
      (EvaluationLink
        (attention-predicate-node "related")
        (ListLink (VariableNode "$A") (VariableNode "$B")))
      (EvaluationLink
        (attention-predicate-node "active")
        (VariableNode "$A")))
    (EvaluationLink
      (attention-predicate-node "inferred")
      (ListLink (VariableNode "$A") (VariableNode "$B")))))

;; Enhanced attention API wrapper functions with ECAN
(define (process-attention-data data)
  "Process data using ECAN attention logic"
  (display "Processing attention data with ECAN: ")
  (display data)
  (newline)
  
  ;; Create attention atom with ECAN values
  (let* ((agent-id (assoc-ref data 'agent-id))
         (importance (assoc-ref data 'importance))
         (urgency (assoc-ref data 'urgency))
         (atom (create-attention-atom agent-id importance urgency 
                                     (* importance 10) ; STI
                                     (* importance 5)))) ; LTI
    ;; Trigger activation spreading
    (spread-activation atom (* importance 0.3) 2)
    atom))

(define (create-attention-atom-simple data)
  "Create AtomSpace representation of attention data (simplified interface)"
  (let ((atom (ConceptNode (string-append "attention:" (object->string data)))))
    (EvaluationLink
      (attention-predicate-node "data")
      (ListLink attention-knowledge-base atom))))

;; ECAN performance testing functions
(define (test-ecan-performance num-agents)
  "Test ECAN performance with multiple agents"
  (display (string-append "Testing ECAN performance with " (number->string num-agents) " agents\n"))
  
  (let ((start-time (current-time))
        (test-requests (map (lambda (i)
                             (list (cons 'agent-id (string-append "agent-" (number->string i)))
                                   (cons 'importance (/ (random 100) 100.0))
                                   (cons 'urgency (/ (random 100) 100.0))))
                           (iota num-agents))))
    
    ;; Process all requests
    (let ((allocation-plan (schedule-attention-resources test-requests)))
      (let ((end-time (current-time))
            (duration-ms (* (- end-time start-time) 1000)))
        
        (display (string-append "ECAN allocation completed in " 
                               (number->string duration-ms) "ms\n"))
        (display (string-append "Processed " (number->string (length allocation-plan)) 
                               " agent allocations\n"))
        
        ;; Return performance metrics
        (list (cons 'duration-ms duration-ms)
              (cons 'agents-processed (length allocation-plan))
              (cons 'sub-50ms-target (< duration-ms 50))
              (cons 'allocation-plan allocation-plan))))))

;; Integration testing functions with ECAN
(define (test-attention-integration)
  "Test enhanced attention integration functionality with ECAN"
  (begin
    (display "Testing ECAN attention integration...\n")
    (initialize-attention)
    
    ;; Test basic ECAN functionality
    (let ((test-data '((agent-id . "test-agent-1") 
                      (importance . 0.8) 
                      (urgency . 0.6))))
      (process-attention-data test-data)
      (create-attention-atom-simple test-data))
    
    ;; Test performance with multiple agents
    (test-ecan-performance 10)
    
    ;; Test rent collection
    (collect-attention-rent)
    
    (display "ECAN attention integration test completed\n")))

;; Export enhanced public API
(export initialize-attention
        query-attention
        process-attention-data  
        create-attention-atom-simple
        test-attention-integration
        ;; ECAN-specific exports
        create-attention-atom
        spread-activation
        collect-attention-rent
        schedule-attention-resources
        start-attention-monitoring
        stop-attention-monitoring
        test-ecan-performance
        get-attention-value)
