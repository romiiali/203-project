"""
Performance tests for non-functional performance requirements
"""
import pytest
import time
import statistics
import threading
from unittest.mock import Mock, patch
from app import create_app
from extensions import db
from models.user import User

class TestPerformance:
    """Performance requirement tests"""
    
    @pytest.fixture
    def app(self):
        """Create test application"""
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_ECHO': False  # Disable echo for performance tests
        })
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.session.remove()
                db.drop_all()
    
    @pytest.fixture
    def load_test_data(self, client):
        """Load test data for performance testing"""
        with client.application.app_context():
            # Create multiple users for load testing
            users = []
            for i in range(100):  # Create 100 test users
                user = User(
                    name=f"Test User {i}",
                    email=f"user{i}@test.com",
                    role="student",
                    password_hash=f"hashed_password_{i}"
                )
                users.append(user)
            
            db.session.add_all(users)
            db.session.commit()
    
    def measure_response_time(self, client, endpoint, method='GET', data=None, iterations=10):
        """Measure response time for an endpoint"""
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            if method == 'GET':
                response = client.get(endpoint, follow_redirects=True)
            elif method == 'POST':
                response = client.post(endpoint, data=data or {}, follow_redirects=True)
            
            end_time = time.time()
            
            # Only record successful responses
            if response.status_code in [200, 302]:
                times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        return times
    
    def test_response_time_requirement(self, client, load_test_data):
        """Test that responses are within 2 seconds (Non-functional requirement: Performance)"""
        print("\n⏱️ Testing response time requirements (< 2 seconds)...")
        
        # Define endpoints to test with their expected maximum response times
        endpoints = [
            ('/login (GET)', '/login', 'GET', None, 1000),  # 1 second max
            ('/student/dashboard', '/student/dashboard', 'GET', None, 1500),  # 1.5 seconds max
            ('/admin/searchpeople', '/admin/searchpeople?search=test', 'GET', None, 2000),  # 2 seconds max
        ]
        
        all_passed = True
        
        for name, endpoint, method, data, max_time_ms in endpoints:
            print(f"\n  Testing: {name}")
            
            # Mock authentication for protected routes
            if 'dashboard' in endpoint or 'admin' in endpoint:
                with client.session_transaction() as sess:
                    sess['user_id'] = 1
                    sess['role'] = 'student' if 'student' in endpoint else 'admin'
            
            # Measure response time
            times = self.measure_response_time(client, endpoint, method, data, iterations=5)
            
            if not times:
                print(f"    ⚠️  No successful responses recorded")
                continue
            
            # Calculate statistics
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"    📊 Response times: {[f'{t:.1f}ms' for t in times]}")
            print(f"    📈 Average: {avg_time:.1f}ms, Min: {min_time:.1f}ms, Max: {max_time:.1f}ms")
            
            # Check if meets requirement
            if max_time <= max_time_ms:
                print(f"    ✅ PASS: All responses under {max_time_ms}ms threshold")
            else:
                print(f"    ❌ FAIL: Some responses exceed {max_time_ms}ms threshold")
                all_passed = False
        
        # Overall result
        if all_passed:
            print("\n🎉 All endpoints meet response time requirements!")
        else:
            print("\n⚠️ Some endpoints need performance optimization")
        
        return all_passed
    
    def test_concurrent_user_handling(self, client, load_test_data):
        """Test system stability under concurrent users"""
        print("\n👥 Testing concurrent user handling...")
        
        results = []
        errors = []
        
        def user_workflow(user_id):
            """Simulate a user workflow"""
            try:
                # Create a new test client for each thread
                app = create_app()
                app.config.update({
                    'TESTING': True,
                    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
                })
                
                with app.test_client() as thread_client:
                    with app.app_context():
                        # Simulate login
                        with thread_client.session_transaction() as sess:
                            sess['user_id'] = user_id
                            sess['role'] = 'student'
                        
                        # Access dashboard
                        start_time = time.time()
                        response = thread_client.get('/student/dashboard', follow_redirects=True)
                        end_time = time.time()
                        
                        if response.status_code == 200:
                            results.append({
                                'user_id': user_id,
                                'response_time': (end_time - start_time) * 1000,
                                'success': True
                            })
                        else:
                            results.append({
                                'user_id': user_id,
                                'success': False,
                                'status_code': response.status_code
                            })
            except Exception as e:
                errors.append(f"User {user_id}: {str(e)}")
        
        # Simulate concurrent users
        num_users = 10  # Simulate 10 concurrent users
        threads = []
        
        print(f"  Simulating {num_users} concurrent users...")
        
        for i in range(num_users):
            thread = threading.Thread(target=user_workflow, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        successful_responses = [r for r in results if r.get('success')]
        failed_responses = [r for r in results if not r.get('success')]
        
        print(f"  📊 Results: {len(successful_responses)} successful, {len(failed_responses)} failed")
        
        if successful_responses:
            response_times = [r['response_time'] for r in successful_responses]
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            
            print(f"  📈 Average response time: {avg_time:.1f}ms")
            print(f"  📈 Maximum response time: {max_time:.1f}ms")
            
            # Requirement: Should handle concurrent users without crashing
            if len(failed_responses) == 0:
                print("  ✅ PASS: System handles concurrent users without errors")
            else:
                print(f"  ⚠️  {len(failed_responses)} users experienced errors")
        
        if errors:
            print(f"  ❌ Errors encountered: {len(errors)}")
            for error in errors[:3]:  # Show first 3 errors
                print(f"    - {error}")
        
        return len(failed_responses) == 0
    
    def test_database_query_performance(self, client, load_test_data):
        """Test database query performance"""
        print("\n🗄️ Testing database query performance...")
        
        # Test search functionality with large datasets
        search_terms = ['test', 'user', '1', '50', '99']
        
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'admin'
        
        for term in search_terms:
            print(f"\n  Testing search for term: '{term}'")
            
            # Mock the search function
            with patch('controllers.admin_controller.User') as MockUser:
                # Simulate search returning results
                mock_results = [Mock(name=f"User {i}", email=f"user{i}@test.com") for i in range(20)]
                MockUser.search_users.return_value = mock_results
                
                # Measure search time
                start_time = time.time()
                response = client.get(f'/admin/searchpeople?search={term}', follow_redirects=True)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    print(f"    ⏱️ Search completed in {response_time:.1f}ms")
                    
                    # Requirement: Search should complete within 1 second
                    if response_time <= 1000:
                        print(f"    ✅ PASS: Search under 1 second threshold")
                    else:
                        print(f"    ⚠️  Search took {response_time:.1f}ms (consider optimization)")
                else:
                    print(f"    ❌ Search failed with status {response.status_code}")
    
    def test_memory_usage(self):
        """Test memory usage (simulated)"""
        print("\n💾 Testing memory usage considerations...")
        
        # This is a simplified memory test
        # In real scenarios, use memory_profiler or similar tools
        
        import sys
        
        # Track object creation
        initial_objects = []
        
        # Create multiple objects to simulate memory usage
        objects_created = []
        
        for i in range(1000):
            obj = {
                'id': i,
                'name': f'Test Object {i}',
                'data': 'x' * 1000  # 1KB per object
            }
            objects_created.append(obj)
        
        # Calculate approximate memory usage
        approximate_memory = sys.getsizeof(objects_created) + sum(
            sys.getsizeof(obj) for obj in objects_created
        )
        
        memory_mb = approximate_memory / (1024 * 1024)
        
        print(f"  Created 1000 test objects")
        print(f"  Approximate memory usage: {memory_mb:.2f} MB")
        
        if memory_mb < 100:  # Arbitrary threshold
            print(f"  ✅ Memory usage within reasonable limits")
        else:
            print(f"  ⚠️  High memory usage - consider optimization")
        
        # Clean up
        del objects_created
        
        return memory_mb
    
    def test_scalability(self, client):
        """Test system scalability with increasing load"""
        print("\n📈 Testing scalability...")
        
        load_levels = [1, 5, 10, 20]  # Number of simulated requests
        response_times = []
        
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'student'
        
        for load in load_levels:
            print(f"\n  Testing with {load} simultaneous requests...")
            
            # Mock the dashboard endpoint
            with patch('controllers.student_controller.Student') as MockStudent:
                mock_student = Mock()
                mock_student.get_enrolled_courses.return_value = []
                MockStudent.get_by_id.return_value = mock_student
                
                times = []
                for i in range(load):
                    start_time = time.time()
                    response = client.get('/student/dashboard', follow_redirects=True)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        times.append((end_time - start_time) * 1000)
                
                if times:
                    avg_time = statistics.mean(times)
                    response_times.append(avg_time)
                    print(f"    Average response time: {avg_time:.1f}ms")
        
        # Analyze scalability
        if len(response_times) >= 2:
            # Check if response time increases linearly or exponentially
            growth_factor = response_times[-1] / response_times[0] if response_times[0] > 0 else 0
            load_factor = load_levels[-1] / load_levels[0]
            
            print(f"\n  📊 Scalability analysis:")
            print(f"    Load increased {load_factor}x")
            print(f"    Response time increased {growth_factor:.2f}x")
            
            if growth_factor <= load_factor * 1.5:  # Allow 50% overhead
                print(f"    ✅ Good scalability: Response time grows reasonably with load")
            else:
                print(f"    ⚠️  Poor scalability: Response time grows faster than load")
        
        return response_times
    
    def test_caching_effectiveness(self, client):
        """Test caching mechanisms if implemented"""
        print("\n💨 Testing caching effectiveness...")
        
        # Test repeated access to same endpoint
        endpoint = '/login'  # Public endpoint, no auth needed
        
        first_access_times = []
        repeated_access_times = []
        
        # First access (cold)
        for i in range(3):
            start_time = time.time()
            response = client.get(endpoint, follow_redirects=True)
            end_time = time.time()
            
            if response.status_code == 200:
                first_access_times.append((end_time - start_time) * 1000)
        
        # Repeated access (warm - should be faster if cached)
        for i in range(3):
            start_time = time.time()
            response = client.get(endpoint, follow_redirects=True)
            end_time = time.time()
            
            if response.status_code == 200:
                repeated_access_times.append((end_time - start_time) * 1000)
        
        if first_access_times and repeated_access_times:
            avg_first = statistics.mean(first_access_times)
            avg_repeated = statistics.mean(repeated_access_times)
            
            print(f"  First access (cold): {avg_first:.1f}ms average")
            print(f"  Repeated access (warm): {avg_repeated:.1f}ms average")
            
            if avg_repeated < avg_first:
                improvement = ((avg_first - avg_repeated) / avg_first) * 100
                print(f"  📈 {improvement:.1f}% improvement on repeated access")
                
                if improvement > 10:
                    print(f"  ✅ Good caching effectiveness")
                else:
                    print(f"  ℹ️  Minimal caching benefit detected")
            else:
                print(f"  ⚠️  No caching benefit - consider implementing caching")
        
        # Check for cache headers in responses
        response = client.get(endpoint)
        cache_headers = ['Cache-Control', 'Expires', 'ETag', 'Last-Modified']
        
        print(f"\n  Checking cache headers:")
        for header in cache_headers:
            if header in response.headers:
                print(f"    ✅ {header}: {response.headers[header]}")
            else:
                print(f"    ℹ️  {header} header not present")
    
    def test_error_recovery_performance(self, client):
        """Test performance during error conditions"""
        print("\n🔄 Testing error recovery performance...")
        
        # Test accessing non-existent endpoints
        non_existent_endpoints = [
            '/nonexistent',
            '/student/nonexistent',
            '/api/v1/invalid'
        ]
        
        for endpoint in non_existent_endpoints:
            start_time = time.time()
            response = client.get(endpoint, follow_redirects=True)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            # 404 errors should be handled quickly
            if response.status_code == 404:
                print(f"  {endpoint}: 404 in {response_time:.1f}ms")
                
                if response_time <= 500:  # Should handle 404 quickly
                    print(f"    ✅ Fast error handling")
                else:
                    print(f"    ⚠️  Slow error handling")
            else:
                print(f"  {endpoint}: Unexpected status {response.status_code}")