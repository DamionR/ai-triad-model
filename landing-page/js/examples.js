/**
 * Examples Page JavaScript
 * Interactive functionality for code examples and demonstrations
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initializeExamples();
});

function initializeExamples() {
    initializeExampleActions();
    initializePlaygrounds();
    initializeExampleSearch();
    initializeTryButtons();
}

/**
 * Example Action Handlers
 */
function initializeExampleActions() {
    const actionButtons = document.querySelectorAll('[data-action]');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const exampleContainer = this.closest('.example-container');
            
            switch (action) {
                case 'copy-example':
                    copyExampleCode(exampleContainer);
                    break;
                case 'run-example':
                    runExampleOnline(exampleContainer);
                    break;
                case 'view-demo':
                    viewExampleDemo(exampleContainer);
                    break;
                case 'view-architecture':
                    viewArchitectureDiagram(exampleContainer);
                    break;
                default:
                    console.log(`Unknown action: ${action}`);
            }
        });
    });
}

/**
 * Copy Example Code
 */
async function copyExampleCode(container) {
    const codeBlock = container.querySelector('.docs-code-block pre code');
    const button = container.querySelector('[data-action="copy-example"]');
    
    if (!codeBlock) return;
    
    try {
        const codeText = codeBlock.textContent;
        await navigator.clipboard.writeText(codeText);
        
        // Visual feedback
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.classList.add('example-copied');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('example-copied');
        }, 2000);
        
    } catch (err) {
        console.error('Failed to copy code:', err);
        
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = codeBlock.textContent;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        // Visual feedback
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    }
}

/**
 * Run Example Online
 */
function runExampleOnline(container) {
    const codeBlock = container.querySelector('.docs-code-block pre code');
    const button = container.querySelector('[data-action="run-example"]');
    
    if (!codeBlock) return;
    
    // Simulate running example online
    button.textContent = 'Running...';
    button.disabled = true;
    
    // Create modal with simulated execution
    const modal = createExecutionModal(codeBlock.textContent);
    document.body.appendChild(modal);
    
    // Simulate execution
    simulateExecution(modal);
    
    // Reset button
    setTimeout(() => {
        button.textContent = 'Try Online';
        button.disabled = false;
    }, 3000);
}

/**
 * Create Execution Modal
 */
function createExecutionModal(code) {
    const modal = document.createElement('div');
    modal.className = 'execution-modal';
    modal.innerHTML = `
        <div class="execution-modal-backdrop"></div>
        <div class="execution-modal-content">
            <div class="execution-modal-header">
                <h3>🚀 Running Example</h3>
                <button class="execution-close">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="execution-modal-body">
                <div class="execution-output" id="executionOutput">
                    <div class="execution-status">Initializing environment...</div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal styles
    const styles = `
        <style>
        .execution-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: var(--space-lg);
        }
        
        .execution-modal-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
        }
        
        .execution-modal-content {
            position: relative;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            width: 90%;
            max-width: 800px;
            max-height: 80vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        }
        
        .execution-modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--space-lg);
            border-bottom: 1px solid var(--border-primary);
            background: var(--bg-primary);
        }
        
        .execution-modal-header h3 {
            color: var(--white);
            margin: 0;
            font-size: 1.25rem;
        }
        
        .execution-close {
            background: none;
            border: none;
            color: var(--gray-400);
            cursor: pointer;
            padding: var(--space-xs);
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
        }
        
        .execution-close:hover {
            color: var(--framework-purple-light);
            background: var(--bg-tertiary);
        }
        
        .execution-modal-body {
            padding: var(--space-lg);
            max-height: 60vh;
            overflow-y: auto;
        }
        
        .execution-output {
            background: var(--bg-primary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-md);
            padding: var(--space-lg);
            font-family: var(--font-mono);
            font-size: 0.875rem;
            line-height: 1.6;
            color: var(--gray-300);
            min-height: 300px;
        }
        
        .execution-status {
            color: var(--framework-purple-light);
            margin-bottom: var(--space-md);
        }
        
        .execution-line {
            margin-bottom: var(--space-sm);
            opacity: 0;
            animation: fadeInLine 0.5s ease forwards;
        }
        
        .execution-success {
            color: #10B981;
        }
        
        .execution-error {
            color: #EF4444;
        }
        
        .execution-info {
            color: var(--system-gold);
        }
        
        @keyframes fadeInLine {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
    `;
    
    modal.insertAdjacentHTML('beforeend', styles);
    
    // Close modal functionality
    modal.addEventListener('click', function(e) {
        if (e.target === modal || e.target.classList.contains('execution-modal-backdrop') || e.target.closest('.execution-close')) {
            document.body.removeChild(modal);
        }
    });
    
    return modal;
}

/**
 * Simulate Code Execution
 */
function simulateExecution(modal) {
    const output = modal.querySelector('#executionOutput');
    
    const executionSteps = [
        { text: "🚀 Initializing AI Triad Model framework...", type: "info", delay: 500 },
        { text: "📦 Loading dependencies...", type: "info", delay: 800 },
        { text: "🔧 Setting up agents...", type: "info", delay: 1000 },
        { text: "  ✓ Planner Agent initialized", type: "success", delay: 1200 },
        { text: "  ✓ Executor Agent initialized", type: "success", delay: 1400 },
        { text: "  ✓ Evaluator Agent initialized", type: "success", delay: 1600 },
        { text: "  ✓ Overwatch Agent initialized", type: "success", delay: 1800 },
        { text: "📝 Processing request through framework...", type: "info", delay: 2000 },
        { text: "🤖 Planner: Creating strategic plan...", type: "info", delay: 2300 },
        { text: "⚙️ Executor: Implementing solution...", type: "info", delay: 2600 },
        { text: "✅ Evaluator: Reviewing quality...", type: "info", delay: 2900 },
        { text: "👁️ Overwatch: Final approval...", type: "info", delay: 3200 },
        { text: "🎉 Execution completed successfully!", type: "success", delay: 3500 },
        { text: "", type: "info", delay: 3600 },
        { text: "Result: Welcome to our platform! We're excited to have you join us.", type: "success", delay: 3700 },
        { text: "System Compliance: True", type: "success", delay: 3800 },
        { text: "Quality Score: 95/100", type: "success", delay: 3900 },
    ];
    
    executionSteps.forEach((step, index) => {
        setTimeout(() => {
            const line = document.createElement('div');
            line.className = `execution-line execution-${step.type}`;
            line.textContent = step.text;
            output.appendChild(line);
            
            // Auto-scroll to bottom
            output.scrollTop = output.scrollHeight;
        }, step.delay);
    });
}

/**
 * View Example Demo
 */
function viewExampleDemo(container) {
    const sectionId = container.closest('.docs-section').id;
    
    // Create demo modal based on example type
    const modal = createDemoModal(sectionId);
    document.body.appendChild(modal);
}

/**
 * Create Demo Modal
 */
function createDemoModal(exampleId) {
    const modal = document.createElement('div');
    modal.className = 'demo-modal';
    
    let demoContent = '';
    
    switch (exampleId) {
        case 'customer-support':
            demoContent = createCustomerSupportDemo();
            break;
        default:
            demoContent = '<p>Demo not available for this example.</p>';
    }
    
    modal.innerHTML = `
        <div class="demo-modal-backdrop"></div>
        <div class="demo-modal-content">
            <div class="demo-modal-header">
                <h3>🎮 Interactive Demo</h3>
                <button class="demo-close">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="demo-modal-body">
                ${demoContent}
            </div>
        </div>
    `;
    
    // Add demo modal styles
    const styles = `
        <style>
        .demo-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: var(--space-lg);
        }
        
        .demo-modal-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
        }
        
        .demo-modal-content {
            position: relative;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            width: 95%;
            max-width: 1000px;
            max-height: 90vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        }
        
        .demo-modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--space-lg);
            border-bottom: 1px solid var(--border-primary);
            background: var(--bg-primary);
        }
        
        .demo-modal-header h3 {
            color: var(--white);
            margin: 0;
            font-size: 1.25rem;
        }
        
        .demo-close {
            background: none;
            border: none;
            color: var(--gray-400);
            cursor: pointer;
            padding: var(--space-xs);
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
        }
        
        .demo-close:hover {
            color: var(--framework-purple-light);
            background: var(--bg-tertiary);
        }
        
        .demo-modal-body {
            padding: var(--space-lg);
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .demo-interface {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--space-xl);
            min-height: 500px;
        }
        
        .demo-input-section {
            background: var(--bg-primary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            padding: var(--space-lg);
        }
        
        .demo-output-section {
            background: var(--bg-primary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            padding: var(--space-lg);
        }
        
        .demo-input {
            width: 100%;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-md);
            padding: var(--space-md);
            color: var(--white);
            min-height: 100px;
            resize: vertical;
            margin-bottom: var(--space-md);
        }
        
        .demo-agent-responses {
            display: grid;
            gap: var(--space-md);
        }
        
        .demo-agent-response {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-md);
            padding: var(--space-md);
        }
        
        .demo-agent-response h5 {
            color: var(--framework-purple-light);
            margin: 0 0 var(--space-sm) 0;
            font-size: 0.875rem;
        }
        
        .demo-agent-response p {
            color: var(--gray-300);
            margin: 0;
            font-size: 0.8125rem;
            line-height: 1.5;
        }
        
        @media (max-width: 768px) {
            .demo-interface {
                grid-template-columns: 1fr;
                gap: var(--space-lg);
            }
        }
        </style>
    `;
    
    modal.insertAdjacentHTML('beforeend', styles);
    
    // Close modal functionality
    modal.addEventListener('click', function(e) {
        if (e.target === modal || e.target.classList.contains('demo-modal-backdrop') || e.target.closest('.demo-close')) {
            document.body.removeChild(modal);
        }
    });
    
    return modal;
}

/**
 * Create Customer Support Demo
 */
function createCustomerSupportDemo() {
    return `
        <div class="demo-interface">
            <div class="demo-input-section">
                <h4 style="color: var(--white); margin-bottom: var(--space-lg);">Customer Support Ticket</h4>
                <textarea class="demo-input" placeholder="Enter customer message..." id="supportInput">I can't access my account and I'm getting frustrated. I've been trying for an hour and keep getting error messages.</textarea>
                <button class="btn btn--primary" onclick="processSupportTicket()">Process Ticket</button>
            </div>
            <div class="demo-output-section">
                <h4 style="color: var(--white); margin-bottom: var(--space-lg);">Agent Responses</h4>
                <div class="demo-agent-responses" id="agentResponses">
                    <div class="demo-agent-response">
                        <h5>System Status</h5>
                        <p>Ready to process customer support request...</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Process Support Ticket (Demo)
 */
window.processSupportTicket = function() {
    const input = document.getElementById('supportInput');
    const output = document.getElementById('agentResponses');
    
    if (!input || !output) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    // Clear output
    output.innerHTML = '';
    
    // Simulate agent processing
    const responses = [
        { agent: 'Planner', message: 'Analyzing customer intent... Issue categorized as: Account Access Problem. Sentiment: Frustrated. Priority: High', delay: 500 },
        { agent: 'Executor', message: 'Generating solution... Checking account status, preparing password reset instructions, and escalation procedures.', delay: 1500 },
        { agent: 'Evaluator', message: 'Reviewing response quality... Tone assessment: Empathetic. Completeness: 95%. Technical accuracy: Verified.', delay: 2500 },
        { agent: 'Overwatch', message: 'Final approval complete. Response approved for delivery. No escalation required. Customer satisfaction probability: 92%', delay: 3500 }
    ];
    
    responses.forEach(response => {
        setTimeout(() => {
            const div = document.createElement('div');
            div.className = 'demo-agent-response';
            div.innerHTML = `
                <h5>${response.agent} Agent</h5>
                <p>${response.message}</p>
            `;
            output.appendChild(div);
        }, response.delay);
    });
    
    // Final response
    setTimeout(() => {
        const div = document.createElement('div');
        div.className = 'demo-agent-response';
        div.style.borderLeft = '4px solid #10B981';
        div.innerHTML = `
            <h5>Final Customer Response</h5>
            <p>Hi there! I understand how frustrating account access issues can be. I've checked your account and can help you get back in right away. I'm sending you a secure password reset link that will resolve this immediately. You should receive it within 2 minutes. If you need any further assistance, I'm here to help!</p>
        `;
        output.appendChild(div);
    }, 4500);
};

/**
 * Initialize Try Buttons
 */
function initializeTryButtons() {
    const tryButtons = document.querySelectorAll('.nav-actions .btn--secondary');
    
    tryButtons.forEach(button => {
        if (button.textContent.includes('Try Example')) {
            button.addEventListener('click', function() {
                // Scroll to first example
                const firstExample = document.getElementById('hello-world');
                if (firstExample) {
                    firstExample.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
    });
}

/**
 * Initialize Playgrounds
 */
function initializePlaygrounds() {
    const playgrounds = document.querySelectorAll('.example-playground');
    
    playgrounds.forEach(playground => {
        const input = playground.querySelector('.playground-input');
        const output = playground.querySelector('.playground-output');
        const runButton = playground.querySelector('.btn--primary');
        
        if (runButton && input && output) {
            runButton.addEventListener('click', function() {
                const code = input.value;
                if (code.trim()) {
                    simulatePlaygroundExecution(output, code);
                }
            });
        }
    });
}

/**
 * Simulate Playground Execution
 */
function simulatePlaygroundExecution(output, code) {
    output.textContent = 'Running code...\n';
    
    setTimeout(() => {
        output.textContent += 'Framework initialized successfully!\n';
        output.textContent += 'Processing request through agents...\n';
        output.textContent += 'Result: Code executed successfully in playground environment.\n';
        output.textContent += 'Note: This is a simulated execution for demonstration purposes.';
    }, 1000);
}

/**
 * Initialize Example Search
 */
function initializeExampleSearch() {
    // Extend the existing search functionality for examples
    const searchButtons = document.querySelectorAll('.nav-actions .btn--secondary');
    
    searchButtons.forEach(button => {
        if (button.textContent.includes('Search')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                // Use the existing search functionality from docs.js
            });
        }
    });
}