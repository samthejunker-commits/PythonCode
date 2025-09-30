import requests
import sys
import json
from datetime import datetime

class ProgramSelectionAPITester:
    def __init__(self, base_url="https://interactive-py-menu.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.program_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, expected_count=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Additional validation for specific endpoints
                if response.status_code == 200 and response.content:
                    try:
                        json_data = response.json()
                        if expected_count and isinstance(json_data, list):
                            if len(json_data) == expected_count:
                                print(f"   ✅ Count validation passed: {len(json_data)} items")
                            else:
                                print(f"   ⚠️  Count mismatch: expected {expected_count}, got {len(json_data)}")
                        
                        # Store program IDs for later tests
                        if endpoint == "programs" and isinstance(json_data, list):
                            self.program_ids = [prog['id'] for prog in json_data]
                            print(f"   📝 Stored {len(self.program_ids)} program IDs")
                            
                        return True, json_data
                    except json.JSONDecodeError:
                        print(f"   ⚠️  Response is not valid JSON")
                        return True, response.text
                else:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.content:
                    try:
                        error_data = response.json()
                        print(f"   Error details: {error_data}")
                    except:
                        print(f"   Error text: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_get_programs(self):
        """Test getting all programs - should return 15 programs"""
        success, response = self.run_test(
            "Get All Programs",
            "GET",
            "programs",
            200,
            expected_count=15
        )
        
        if success and isinstance(response, list):
            # Validate program structure
            for i, program in enumerate(response):
                expected_name = f"Prg{i+1}"
                if program.get('name') != expected_name:
                    print(f"   ⚠️  Program {i+1} name mismatch: expected {expected_name}, got {program.get('name')}")
                
                expected_desc = "This is a testing program and soon it will be a program to execute to complete a specific functionality. To be determined soon...."
                if program.get('description') != expected_desc:
                    print(f"   ⚠️  Program {i+1} description mismatch")
                
                required_fields = ['id', 'name', 'title', 'description', 'created_at']
                for field in required_fields:
                    if field not in program:
                        print(f"   ⚠️  Program {i+1} missing field: {field}")
        
        return success

    def test_get_single_program(self):
        """Test getting a single program by ID"""
        if not self.program_ids:
            print("❌ No program IDs available for single program test")
            return False
            
        # Test with first program ID
        program_id = self.program_ids[0]
        success, response = self.run_test(
            f"Get Single Program (ID: {program_id[:8]}...)",
            "GET",
            f"programs/{program_id}",
            200
        )
        
        if success and isinstance(response, dict):
            if response.get('id') != program_id:
                print(f"   ⚠️  ID mismatch: expected {program_id}, got {response.get('id')}")
        
        return success

    def test_get_nonexistent_program(self):
        """Test getting a program that doesn't exist"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        success, response = self.run_test(
            "Get Non-existent Program",
            "GET",
            f"programs/{fake_id}",
            404
        )
        return success

    def test_select_program(self):
        """Test selecting a program"""
        if not self.program_ids:
            print("❌ No program IDs available for program selection test")
            return False
            
        program_id = self.program_ids[0]
        selection_data = {
            "program_id": program_id,
            "program_name": "Prg1",
            "user_session": f"test_session_{datetime.now().strftime('%H%M%S')}"
        }
        
        success, response = self.run_test(
            "Select Program",
            "POST",
            "select-program",
            200,
            data=selection_data
        )
        
        if success and isinstance(response, dict):
            if response.get('program_id') != program_id:
                print(f"   ⚠️  Selection program_id mismatch")
            if 'id' not in response:
                print(f"   ⚠️  Selection missing ID field")
            if 'selected_at' not in response:
                print(f"   ⚠️  Selection missing selected_at field")
        
        return success

    def test_select_nonexistent_program(self):
        """Test selecting a program that doesn't exist"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        selection_data = {
            "program_id": fake_id,
            "program_name": "FakeProgram",
            "user_session": "test_session"
        }
        
        success, response = self.run_test(
            "Select Non-existent Program",
            "POST",
            "select-program",
            404,
            data=selection_data
        )
        return success

    def test_get_selections(self):
        """Test getting all program selections"""
        success, response = self.run_test(
            "Get All Selections",
            "GET",
            "selections",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   📊 Found {len(response)} selections in database")
            if len(response) > 0:
                selection = response[0]
                required_fields = ['id', 'program_id', 'program_name', 'selected_at']
                for field in required_fields:
                    if field not in selection:
                        print(f"   ⚠️  Selection missing field: {field}")
        
        return success

def main():
    print("🚀 Starting Program Selection API Tests")
    print("=" * 50)
    
    tester = ProgramSelectionAPITester()
    
    # Run all tests in sequence
    tests = [
        tester.test_root_endpoint,
        tester.test_get_programs,
        tester.test_get_single_program,
        tester.test_get_nonexistent_program,
        tester.test_select_program,
        tester.test_select_nonexistent_program,
        tester.test_get_selections
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())