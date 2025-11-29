"""
Quick verification script - Run this after deployment
Tests the complete chat flow end-to-end
"""

import requests
import json
import time
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")


def test_health(base_url):
    """Test health endpoint"""
    print(f"\n{Colors.BOLD}Testing Health Endpoint...{Colors.RESET}")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print_success("Health endpoint responding")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False


def register_user(base_url):
    """Register a test user"""
    print(f"\n{Colors.BOLD}Registering Test User...{Colors.RESET}")
    
    timestamp = int(time.time())
    user_data = {
        "email": f"test_{timestamp}@example.com",
        "password": "testpass123",
        "name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/register",
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success(f"User registered: {user_data['email']}")
            return user_data
        elif response.status_code == 400 and "already registered" in response.text.lower():
            print_warning("User already exists, will try login")
            return user_data
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None


def login_user(base_url, user_data):
    """Login and get JWT token"""
    print(f"\n{Colors.BOLD}Logging In...{Colors.RESET}")
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_success(f"Login successful")
            print_info(f"Token: {token[:20]}...")
            return token
        else:
            print_error(f"Login failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None


def test_chat_without_documents(base_url, token):
    """Test chat endpoint without uploaded documents"""
    print(f"\n{Colors.BOLD}Testing Chat (No Documents)...{Colors.RESET}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    chat_request = {
        "message": "What is machine learning?",
        "use_rag": True,
        "rag_mode": "fast",
        "include_citations": True,
        "check_safety": False
    }
    
    try:
        print_info("Sending chat request...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/chat/v2/message",
            headers=headers,
            json=chat_request,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", "")
            sources = data.get("sources", [])
            model_used = data.get("model_used", "unknown")
            
            print_success(f"Chat response received ({elapsed:.2f}s)")
            print_info(f"Model used: {model_used}")
            print_info(f"Sources: {len(sources)}")
            print_info(f"Response preview: {message[:100]}...")
            
            # Check if we got the expected "no documents" message
            if "don't have any relevant information" in message.lower() or len(sources) == 0:
                print_success("Got expected response (no documents uploaded)")
            else:
                print_warning("Got response with sources (unexpected)")
            
            return True
        else:
            print_error(f"Chat failed: {response.status_code}")
            print_error(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Chat request timed out (>30s)")
        return False
    except Exception as e:
        print_error(f"Chat error: {str(e)}")
        return False


def test_chat_with_gemini_error_handling(base_url, token):
    """Test that error handling works properly"""
    print(f"\n{Colors.BOLD}Testing Error Handling...{Colors.RESET}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Send a request that might trigger errors
    chat_request = {
        "message": "This is a very long query " * 100,  # Try to trigger issues
        "use_rag": True,
        "rag_mode": "accurate",
        "include_citations": True,
        "check_safety": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/v2/message",
            headers=headers,
            json=chat_request,
            timeout=30
        )
        
        if response.status_code == 200:
            print_success("Error handling working - got successful response")
            return True
        elif response.status_code == 500:
            print_error("Got 500 error - error handling NOT working!")
            return False
        else:
            print_warning(f"Got {response.status_code} - may be expected")
            return True
            
    except Exception as e:
        print_error(f"Error handling test failed: {str(e)}")
        return False


def run_all_tests(base_url):
    """Run complete test suite"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}🧪 RegnovaClean Verification Tests{Colors.RESET}")
    print("="*60)
    print(f"Base URL: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    
    # Test 1: Health
    results["Health Check"] = test_health(base_url)
    
    if not results["Health Check"]:
        print_error("\nHealth check failed. Cannot proceed with other tests.")
        return results
    
    # Test 2: Registration
    user_data = register_user(base_url)
    results["User Registration"] = user_data is not None
    
    if not results["User Registration"]:
        print_error("\nUser registration failed. Cannot proceed.")
        return results
    
    # Test 3: Login
    token = login_user(base_url, user_data)
    results["User Login"] = token is not None
    
    if not results["User Login"]:
        print_error("\nLogin failed. Cannot proceed.")
        return results
    
    # Test 4: Chat without documents
    results["Chat Endpoint"] = test_chat_without_documents(base_url, token)
    
    # Test 5: Error handling
    results["Error Handling"] = test_chat_with_gemini_error_handling(base_url, token)
    
    # Summary
    print("\n" + "="*60)
    print(f"{Colors.BOLD}📊 Test Results Summary{Colors.RESET}")
    print("="*60)
    
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    passed = sum(results.values())
    total = len(results)
    
    print("="*60)
    print(f"{Colors.BOLD}Score: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.RESET}")
        print("Your deployment is working correctly.")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  SOME TESTS FAILED{Colors.RESET}")
        print("Please review the errors above and check:")
        print("1. Environment variables are set correctly")
        print("2. Gemini API key is valid")
        print("3. Server logs for detailed errors")
    
    print("="*60)
    
    return results


if __name__ == "__main__":
    import sys
    
    # Get base URL from command line or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        # Default to localhost
        base_url = "http://localhost:8000"
        print(f"\n{Colors.YELLOW}No URL provided. Using default: {base_url}{Colors.RESET}")
        print(f"{Colors.YELLOW}To test Render deployment, run:{Colors.RESET}")
        print(f"  python verify_deployment.py https://your-app.onrender.com\n")
    
    try:
        results = run_all_tests(base_url)
        
        # Exit with appropriate code
        all_passed = all(results.values())
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
