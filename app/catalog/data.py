# Curated SHL Assessment Catalog Database
# Based on official SHL Individual Test Solutions
SHL_CATALOG = {
    "K": {
        "name": "Knowledge Tests",
        "assessments": [
            {
                "name": "Java 8",
                "code": "JAVA8",
                "url": "https://www.shl.com/solutions/products/java/",
                "type": "K",
                "domain": "Technical Knowledge",
                "description": "Assesses Java programming knowledge and practical coding skills",
                "skills": ["Java", "Programming", "Technical"],
                "seniority": ["Entry", "Mid", "Senior"]
            },
            {
                "name": "Python",
                "code": "PYTHON",
                "url": "https://www.shl.com/solutions/products/python/",
                "type": "K",
                "domain": "Technical Knowledge",
                "description": "Evaluates Python programming competency",
                "skills": ["Python", "Programming", "Technical"],
                "seniority": ["Entry", "Mid", "Senior"]
            },
            {
                "name": "SQL",
                "code": "SQL",
                "url": "https://www.shl.com/solutions/products/sql/",
                "type": "K",
                "domain": "Technical Knowledge",
                "description": "Tests database query and SQL expertise",
                "skills": ["SQL", "Database", "Technical"],
                "seniority": ["Entry", "Mid", "Senior"]
            },
            {
                "name": "JavaScript",
                "code": "JS",
                "url": "https://www.shl.com/solutions/products/javascript/",
                "type": "K",
                "domain": "Technical Knowledge",
                "description": "Assesses JavaScript and web development knowledge",
                "skills": ["JavaScript", "Web", "Programming"],
                "seniority": ["Entry", "Mid", "Senior"]
            },
            {
                "name": "C++",
                "code": "CPP",
                "url": "https://www.shl.com/solutions/products/cpp/",
                "type": "K",
                "domain": "Technical Knowledge",
                "description": "Evaluates C++ programming skills",
                "skills": ["C++", "Systems", "Programming"],
                "seniority": ["Mid", "Senior"]
            },
            {
                "name": "AWS Solutions Architect",
                "code": "AWS",
                "url": "https://www.shl.com/solutions/products/aws/",
                "type": "K",
                "domain": "Cloud Knowledge",
                "description": "Tests AWS cloud architecture knowledge",
                "skills": ["AWS", "Cloud", "Architecture"],
                "seniority": ["Mid", "Senior"]
            },
            {
                "name": "Accounting Fundamentals",
                "code": "ACCT",
                "url": "https://www.shl.com/solutions/products/accounting/",
                "type": "K",
                "domain": "Finance",
                "description": "Assesses accounting and financial principles",
                "skills": ["Accounting", "Finance", "Analysis"],
                "seniority": ["Entry", "Mid"]
            }
        ]
    },
    "P": {
        "name": "Personality & Behavioral",
        "assessments": [
            {
                "name": "OPQ32r",
                "code": "OPQ32R",
                "url": "https://www.shl.com/solutions/products/opq32r/",
                "type": "P",
                "domain": "Personality",
                "description": "Comprehensive personality assessment measuring 32 dimensions",
                "dimensions": ["Leadership", "Team Work", "Motivation", "Emotional Control"],
                "use_cases": ["Leadership", "Team Fit", "Cultural Alignment"]
            },
            {
                "name": "CAPP",
                "code": "CAPP",
                "url": "https://www.shl.com/solutions/products/capp/",
                "type": "P",
                "domain": "Personality",
                "description": "Competency-based personality assessment for fit analysis",
                "dimensions": ["Agility", "Collaboration", "Decisiveness"],
                "use_cases": ["Role Fit", "Team Dynamics"]
            },
            {
                "name": "CPI 260",
                "code": "CPI260",
                "url": "https://www.shl.com/solutions/products/cpi260/",
                "type": "P",
                "domain": "Personality",
                "description": "Leadership and interpersonal style assessment",
                "dimensions": ["Leadership", "Interpersonal Skills", "Values"],
                "use_cases": ["Executive Selection", "Development"]
            },
            {
                "name": "HPI",
                "code": "HPI",
                "url": "https://www.shl.com/solutions/products/hpi/",
                "type": "P",
                "domain": "Personality",
                "description": "Hogan Personality Inventory for normal range personality",
                "dimensions": ["Adjustment", "Ambition", "Prudence"],
                "use_cases": ["Sales", "Customer Service", "Management"]
            }
        ]
    },
    "A": {
        "name": "Ability Tests",
        "assessments": [
            {
                "name": "GSA",
                "code": "GSA",
                "url": "https://www.shl.com/solutions/products/gsa/",
                "type": "A",
                "domain": "General Ability",
                "description": "General and Situational Ability tests for verbal, numerical, abstract reasoning",
                "subtests": ["Verbal Reasoning", "Numerical Reasoning", "Abstract Reasoning"],
                "seniority": ["Entry", "Mid", "Senior"],
                "use_cases": ["Graduate Programs", "Early Career"]
            },
            {
                "name": "DPAT+",
                "code": "DPAT",
                "url": "https://www.shl.com/solutions/products/dpat/",
                "type": "A",
                "domain": "General Ability",
                "description": "Dynamic Personality and Ability Test for mobile-first assessment",
                "subtests": ["Verbal", "Numerical", "Logical"],
                "seniority": ["Entry", "Mid"],
                "use_cases": ["Volume Hiring", "Remote Assessment"]
            },
            {
                "name": "CLET",
                "code": "CLET",
                "url": "https://www.shl.com/solutions/products/clet/",
                "type": "A",
                "domain": "General Ability",
                "description": "Cognitive Ability and Learning Potential for non-verbal assessment",
                "subtests": ["Pattern Recognition", "Spatial Ability"],
                "seniority": ["Entry", "Mid"],
                "use_cases": ["Manufacturing", "Technical Roles"]
            },
            {
                "name": "CLT",
                "code": "CLT",
                "url": "https://www.shl.com/solutions/products/clt/",
                "type": "A",
                "domain": "General Ability",
                "description": "Cognitive Learning Test for reasoning and problem-solving",
                "subtests": ["Inductive Reasoning", "Deductive Reasoning"],
                "seniority": ["Entry", "Mid"],
                "use_cases": ["Analytical Roles", "Problem Solving"]
            },
            {
                "name": "Situational Judgment Test",
                "code": "SJT",
                "url": "https://www.shl.com/solutions/products/situational-judgment/",
                "type": "A",
                "domain": "Judgment",
                "description": "Role-specific situational judgment scenarios",
                "use_cases": ["Customer Service", "Leadership", "Teamwork"]
            }
        ]
    },
    "I": {
        "name": "Industry-Specific",
        "assessments": [
            {
                "name": "Customer Service Aptitude",
                "code": "CSA",
                "url": "https://www.shl.com/solutions/products/customer-service/",
                "type": "I",
                "domain": "Service Industry",
                "description": "Measures customer service competencies and communication",
                "skills": ["Customer Service", "Communication", "Empathy"],
                "roles": ["Customer Service", "Support", "Sales"]
            },
            {
                "name": "Safety Culture Assessment",
                "code": "SCA",
                "url": "https://www.shl.com/solutions/products/safety-culture/",
                "type": "I",
                "domain": "Safety",
                "description": "Evaluates safety awareness and risk management behavior",
                "skills": ["Safety", "Risk Management", "Compliance"],
                "roles": ["Manufacturing", "Construction", "Operations"]
            },
            {
                "name": "Driving Aptitude",
                "code": "DRV",
                "url": "https://www.shl.com/solutions/products/driving-aptitude/",
                "type": "I",
                "domain": "Transport",
                "description": "Assesses driving safety awareness and vehicle operation knowledge",
                "skills": ["Safety", "Vehicle Operation", "Compliance"],
                "roles": ["Driver", "Delivery", "Logistics"]
            },
            {
                "name": "Sales Competency",
                "code": "SALES",
                "url": "https://www.shl.com/solutions/products/sales-competency/",
                "type": "I",
                "domain": "Sales",
                "description": "Evaluates sales skills and customer engagement capabilities",
                "skills": ["Sales", "Persuasion", "Relationship Building"],
                "roles": ["Sales Representative", "Account Executive"]
            }
        ]
    }
}
