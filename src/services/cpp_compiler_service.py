# services/cpp_compiler_service.py
import requests
import json
import base64
import time
import logging

logger = logging.getLogger(__name__)

class CPPCompilerService:
    """Service to compile and run C++ code using online APIs."""
    
    def __init__(self):
        # JDoodle API (Free tier: 200 calls/day)
        self.jdoodle_client_id = "3ffd5306064a5fad897f779e93b25c1c"
        self.jdoodle_client_secret = "57b70e859636d3eb4563615a9c667ac28ef2bd8d01fadbea7073a20cbbf4f108"
        
        # Judge0 API - Free public instance (no API key required)
        self.judge0_base_url = "https://judge0-ce.p.rapidapi.com"
        self.judge0_headers = {
            "X-RapidAPI-Key": "c1ae4e9413msha2979c54edc3ce7p156115jsnc7293a3d3ab4",
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        # Fixed URL format - remove spaces and ensure proper format
        self.judge0_free_url = "https://judge0-ce.p.rapidapi.com"
        
        # Alternative free APIs
        self.codex_api_url = "https://codexapi.vercel.app"
        self.onecompiler_api_url = "https://onecompiler.com/api/code/exec"
    
    def compile_and_run_jdoodle(self, code, input_data=""):
        """
        Compile and run C++ code using JDoodle API.
        
        Args:
            code (str): C++ source code
            input_data (str): Input for the program
            
        Returns:
            dict: Result containing output, error, etc.
        """
        try:
            url = "https://api.jdoodle.com/v1/execute"
            
            payload = {
                "clientId": self.jdoodle_client_id,
                "clientSecret": self.jdoodle_client_secret,
                "script": code,
                "stdin": input_data,
                "language": "cpp17",
                "versionIndex": "0"
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "output": result.get("output", ""),
                    "error": result.get("error", ""),
                    "memory": result.get("memory", ""),
                    "cpuTime": result.get("cpuTime", "")
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"JDoodle compilation error: {str(e)}")
            return {
                "success": False,
                "error": f"JDoodle compilation failed: {str(e)}"
            }
    
    def compile_and_run_codex(self, code, input_data=""):
        """
        Compile and run C++ code using Codex API (alternative free service).
        
        Args:
            code (str): C++ source code
            input_data (str): Input for the program
            
        Returns:
            dict: Result containing output, error, etc.
        """
        try:
            url = f"{self.codex_api_url}/api/v1/execute"
            
            payload = {
                "language": "cpp",
                "code": code,
                "input": input_data
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": result.get("success", False),
                    "output": result.get("output", ""),
                    "error": result.get("error", ""),
                    "time": result.get("time", ""),
                    "memory": result.get("memory", "")
                }
            else:
                return {
                    "success": False,
                    "error": f"Codex API Error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Codex compilation error: {str(e)}")
            return {
                "success": False,
                "error": f"Codex compilation failed: {str(e)}"
            }
    
    def compile_and_run_onecompiler(self, code, input_data=""):
        """
        Compile and run C++ code using OneCompiler API.
        
        Args:
            code (str): C++ source code
            input_data (str): Input for the program
            
        Returns:
            dict: Result containing output, error, etc.
        """
        try:
            payload = {
                "language": "cpp",
                "code": code,
                "stdin": input_data
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.onecompiler_api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": result.get("status") == "success",
                    "output": result.get("stdout", ""),
                    "error": result.get("stderr", "") or result.get("exception", ""),
                    "time": result.get("executionTime", ""),
                    "memory": result.get("memory", "")
                }
            else:
                return {
                    "success": False,
                    "error": f"OneCompiler API Error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"OneCompiler compilation error: {str(e)}")
            return {
                "success": False,
                "error": f"OneCompiler compilation failed: {str(e)}"
            }
    
    def compile_and_run_simple(self, code, input_data=""):
        """
        Simple compilation using a more reliable free service.
        
        Args:
            code (str): C++ source code
            input_data (str): Input for the program
            
        Returns:
            dict: Result containing output, error, etc.
        """
        try:
            # Use a simpler API endpoint
            url = "https://api.programiz.com/compiler-api/compile-and-run"
            
            payload = {
                "language": "cpp",
                "code": code,
                "input": input_data
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": not result.get("error"),
                    "output": result.get("output", ""),
                    "error": result.get("error", ""),
                    "time": result.get("time", ""),
                    "memory": result.get("memory", "")
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Simple compilation error: {str(e)}")
            return {
                "success": False,
                "error": f"Simple compilation failed: {str(e)}"
            }
    
    def compile_and_run_judge0_fixed(self, code, input_data=""):
        """
        Fixed Judge0 implementation with proper URL handling.
        
        Args:
            code (str): C++ source code
            input_data (str): Input for the program
            
        Returns:
            dict: Result containing output, error, etc.
        """
        try:
            # Use the official Judge0 API with proper URL
            base_url = "https://judge0-ce.p.rapidapi.com"
            
            # Submit code for execution
            submit_url = f"{base_url}/submissions?base64_encoded=false&wait=true"
            
            payload = {
                "source_code": code,
                "language_id": 54,  # C++ (GCC 9.2.0)
                "stdin": input_data
            }
            
            headers = {
                "X-RapidAPI-Key": self.judge0_headers["X-RapidAPI-Key"],
                "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            response = requests.post(submit_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 201 or response.status_code == 200:
                result = response.json()
                
                # Extract result
                success = result.get("status", {}).get("id") == 3  # Accepted
                output = result.get("stdout", "") or ""
                error_output = result.get("stderr", "") or ""
                compile_output = result.get("compile_output", "") or ""
                
                # Combine errors
                full_error = ""
                if compile_output:
                    full_error += f"Compile Error: {compile_output}\n"
                if error_output:
                    full_error += f"Runtime Error: {error_output}"
                
                return {
                    "success": success,
                    "output": output,
                    "error": full_error.strip(),
                    "status": result.get("status", {}).get("description", ""),
                    "time": result.get("time", ""),
                    "memory": result.get("memory", "")
                }
            else:
                return {
                    "success": False,
                    "error": f"Judge0 API Error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Judge0 fixed compilation error: {str(e)}")
            return {
                "success": False,
                "error": f"Judge0 compilation failed: {str(e)}"
            }
    
    def compile_and_run(self, code, input_data=""):
        """
        Compile and run C++ code using multiple APIs with fallback.
        
        Args:
            code (str): C++ source code
            input_data (str): Input for the program
            
        Returns:
            dict: Result containing output, error, etc.
        """
        # List of compilation methods to try in order
        methods = [
            ("JDoodle", self.compile_and_run_jdoodle),
            ("Judge0", self.compile_and_run_judge0_fixed),
            ("Simple", self.compile_and_run_simple),
        ]
        
        last_error = ""
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name} compilation service...")
                result = method_func(code, input_data)
                
                if result.get("success"):
                    logger.info(f"{method_name} compilation successful!")
                    return result
                else:
                    last_error = result.get("error", f"{method_name} failed")
                    logger.warning(f"{method_name} failed: {last_error}")
                    continue
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"{method_name} threw exception: {last_error}")
                continue
        
        # If all methods fail
        return {
            "success": False,
            "error": f"All compilation services failed. Last error: {last_error}"
        }

# Sample competitive programming problems and solutions
SAMPLE_PROBLEMS = [
    {
        "title": "Hello World",
        "difficulty": "Beginner",
        "description": "Write a program that prints 'Hello, World!' to the console.",
        "sample_input": "",
        "expected_output": "Hello, World!",
        "starter_code": '''#include <iostream>
using namespace std;

int main() {
    // Your code here
    cout << "Hello, World!" << endl;
    return 0;
}''',
        "solution": '''#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}''',
        "explanation": "This is the simplest C++ program. We include iostream for input/output operations, use the std namespace, and print using cout."
    },
    {
        "title": "Sum of Two Numbers",
        "difficulty": "Beginner",
        "description": "Read two integers and print their sum.",
        "sample_input": "5 3",
        "expected_output": "8",
        "starter_code": '''#include <iostream>
using namespace std;

int main() {
    int a, b;
    // Read two integers
    cin >> a >> b;
    
    // Calculate and print sum
    cout << a + b << endl;
    
    return 0;
}''',
        "solution": '''#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}''',
        "explanation": "We read two integers using cin and print their sum using cout. This demonstrates basic input/output operations."
    },
    {
        "title": "Maximum of Three Numbers",
        "difficulty": "Beginner",
        "description": "Given three integers, find and print the maximum.",
        "sample_input": "10 25 15",
        "expected_output": "25",
        "starter_code": '''#include <iostream>
using namespace std;

int main() {
    int a, b, c;
    cin >> a >> b >> c;
    
    // Find maximum of three numbers
    int max_num = a;
    if (b > max_num) max_num = b;
    if (c > max_num) max_num = c;
    
    cout << max_num << endl;
    return 0;
}''',
        "solution": '''#include <iostream>
using namespace std;

int main() {
    int a, b, c;
    cin >> a >> b >> c;
    
    int max_num = a;
    if (b > max_num) max_num = b;
    if (c > max_num) max_num = c;
    
    cout << max_num << endl;
    return 0;
}''',
        "explanation": "We use conditional statements to compare three numbers and find the maximum. This introduces if statements and comparison operators."
    },
    {
        "title": "Array Sum",
        "difficulty": "Intermediate",
        "description": "Read n integers and print their sum.",
        "sample_input": "5\n1 2 3 4 5",
        "expected_output": "15",
        "starter_code": '''#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    int sum = 0;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        sum += x;
    }
    
    cout << sum << endl;
    return 0;
}''',
        "solution": '''#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    int sum = 0;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        sum += x;
    }
    
    cout << sum << endl;
    return 0;
}''',
        "explanation": "This problem introduces loops and array processing. We read n numbers and calculate their sum using a for loop."
    }
]

def get_learning_path():
    """Get structured learning path for competitive programming."""
    return {
        
        "beginner": {
            "title": "Beginner Level",
            "topics": [
                "Basic Input/Output",
                "Variables and Data Types",
                "Conditional Statements",
                "Loops (for, while)",
                "Arrays and Strings",
                "Functions"
            ],
            "problems": [p for p in SAMPLE_PROBLEMS if p["difficulty"] == "Beginner"]
        },
        "intermediate": {
            "title": "Intermediate Level", 
            "topics": [
                "STL (Standard Template Library)",
                "Sorting and Searching",
                "Basic Graph Algorithms",
                "Dynamic Programming Basics",
                "Greedy Algorithms",
                "Mathematical Concepts"
            ],
            "problems": [p for p in SAMPLE_PROBLEMS if p["difficulty"] == "Intermediate"]
        },
        "advanced": {
            "title": "Advanced Level",
            "topics": [
                "Advanced Data Structures",
                "Complex Graph Algorithms",
                "Advanced Dynamic Programming",
                "Number Theory",
                "Geometry",
                "String Algorithms"
            ],
            "problems": []
        }
    }

def get_cpp_basics():
    """Get C++ basics tutorial content."""
    return {
         "what is competetive programming": {
        "title": "What is Competitive Programming?",
        "content": """
**Definition**:
Competitive programming is a mental sport that involves solving well-defined algorithmic problems using programming, under strict time and memory constraints.

**Advantages**:
- Improves problem-solving and algorithmic thinking
- Enhances speed, accuracy, and code efficiency
- Strengthens understanding of data structures
- Builds persistence and debugging ability

**Applications**:
- Useful in technical interviews and coding assessments
- Helps in tackling real-world optimization problems
- Applied in contests like Codeforces, LeetCode, AtCoder, and ICPC

**Why It's Used in Hiring**:
- Assesses candidate's coding and logical thinking skills
- Tests ability to work under pressure
- Filters technically sound and efficient programmers
- Demonstrates familiarity with standard algorithms and edge-case handling
"""
    },

        "setup": {
            "title": "Setting Up C++",
            "content": """
1. **Online Compilers** (Recommended for beginners):
   - CodeChef IDE
   - HackerRank Code Editor
   - Codeforces Problem Setter
   
2. **Local Setup**:
   - Install GCC compiler
   - Use VS Code with C++ extension
   - Install Code::Blocks or Dev-C++

3. **Compilation Command**:
   ```bash
   g++ -o program program.cpp
   ./program
   ```
"""
        },
        "syntax": {
            "title": "Basic C++ Syntax",
            "content": """
**Basic Structure:**
```cpp
#include <iostream>
using namespace std;

int main() {
    // Your code here
    return 0;
}
```

**Common Headers:**
- `#include <iostream>` - Input/Output
- `#include <vector>` - Dynamic Arrays
- `#include <algorithm>` - Sorting, Searching
- `#include <string>` - String Operations
- `#include <cmath>` - Mathematical Functions
"""
        },
        "tips": {
            "title": "Competitive Programming Tips",
            "content": """
1. **Fast I/O**:
   ```cpp
   ios_base::sync_with_stdio(false);
   cin.tie(NULL);
   ```

2. **Use `long long` for large numbers**

3. **Common Patterns**:
   - Always handle edge cases
   - Use 1-indexed arrays when needed
   - Prefer STL containers and algorithms

4. **Debugging**:
   - Add debug prints
   - Test with sample inputs
   - Check for integer overflow
"""
        }
    }