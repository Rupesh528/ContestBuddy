import requests
import json
from bs4 import BeautifulSoup
from .base_analyzer import BaseProfileAnalyzer
from datetime import datetime

class LeetcodeAnalyzer(BaseProfileAnalyzer):
    def __init__(self):
        super().__init__()
        self.base_url = "https://leetcode.com"
        self.api_url = "https://leetcode.com/graphql"
    
    def get_profile(self, username):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Content-Type': 'application/json',
                'Referer': f'https://leetcode.com/{username}/'
            }
            
            # GraphQL query to get user profile data
            profile_query = {
                "query": """
                query getUserProfile($username: String!) {
                    matchedUser(username: $username) {
                        username
                        profile {
                            realName
                            aboutMe
                            userAvatar
                            ranking
                            reputation
                            starRating
                            location
                            websites
                        }
                        submitStats {
                            acSubmissionNum {
                                difficulty
                                count
                                submissions
                            }
                            totalSubmissionNum {
                                difficulty
                                count
                                submissions
                            }
                        }
                    }
                    userContestRanking(username: $username) {
                        attendedContestsCount
                        rating
                        globalRanking
                        totalParticipants
                        topPercentage
                    }
                    userContestRankingHistory(username: $username) {
                        attended
                        trendDirection
                        problemsSolved
                        totalProblems
                        finishTimeInSeconds
                        rating
                        ranking
                        contest {
                            title
                            startTime
                        }
                    }
                }
                """,
                "variables": {
                    "username": username
                }
            }
            
            # Request profile data
            profile_response = requests.post(
                self.api_url,
                headers=headers,
                json=profile_query,
                timeout=self.timeout
            )
            
            if profile_response.status_code != 200:
                return self.format_error('Failed to fetch LeetCode profile')
            
            profile_data = profile_response.json()
            
            # Check if user exists
            if 'errors' in profile_data or not profile_data.get('data', {}).get('matchedUser'):
                return self.format_error('LeetCode user not found')
            
            # Extract user data
            user_data = profile_data['data']['matchedUser']
            contest_ranking = profile_data['data']['userContestRanking']
            contest_history = profile_data['data']['userContestRankingHistory']
            
            # Get solved problems by difficulty
            solved_problems = {}
            total_solved = 0
            if user_data.get('submitStats', {}).get('acSubmissionNum'):
                for item in user_data['submitStats']['acSubmissionNum']:
                    difficulty = item['difficulty']
                    count = item['count']
                    solved_problems[difficulty] = count
                    if difficulty != 'All':
                        total_solved += count
            
            # Get total submissions
            total_submissions = 0
            if user_data.get('submitStats', {}).get('totalSubmissionNum'):
                for item in user_data['submitStats']['totalSubmissionNum']:
                    if item['difficulty'] == 'All':
                        total_submissions = item['count']
                        break
            
            # Calculate acceptance rate
            acceptance_rate = 0
            if total_submissions > 0:
                acceptance_rate = round((solved_problems.get('All', 0) / total_submissions) * 100, 2)
            
            # Format contest history
            recent_contests = []
            if contest_history:
                for contest in contest_history[:5]:  # Last 5 contests
                    contest_title = contest['contest']['title']
                    contest_date = datetime.fromtimestamp(contest['contest']['startTime']).strftime('%Y-%m-%d')
                    ranking = contest['ranking']
                    rating = contest['rating']
                    problems_solved = contest['problemsSolved']
                    total_problems = contest['totalProblems']
                    
                    recent_contests.append({
                        'name': contest_title,
                        'date': contest_date,
                        'rank': f"#{ranking}" if ranking else 'Unranked',
                        'rating': rating,
                        'problems_solved': f"{problems_solved}/{total_problems}"
                    })
            
            # Get profile picture
            profile_pic = user_data.get('profile', {}).get('userAvatar', '')
            if not profile_pic.startswith(('http://', 'https://')):
                profile_pic = f"https://assets.leetcode.com/users/{username}/{profile_pic}" if profile_pic else ""
            
            # Build the final profile data structure
            return {
                'username': username,
                'real_name': user_data.get('profile', {}).get('realName', ''),
                'about': user_data.get('profile', {}).get('aboutMe', ''),
                'location': user_data.get('profile', {}).get('location', ''),
                'profile_picture': profile_pic,
                'ranking': user_data.get('profile', {}).get('ranking', 0),
                'reputation': user_data.get('profile', {}).get('reputation', 0),
                'star_rating': user_data.get('profile', {}).get('starRating', 0),
                'total_problems_solved': solved_problems.get('All', 0),
                'easy_problems_solved': solved_problems.get('Easy', 0),
                'medium_problems_solved': solved_problems.get('Medium', 0),
                'hard_problems_solved': solved_problems.get('Hard', 0),
                'acceptance_rate': acceptance_rate,
                'total_submissions': total_submissions,
                'contest_rating': contest_ranking.get('rating', 0) if contest_ranking else 0,
                'contest_global_ranking': contest_ranking.get('globalRanking', 0) if contest_ranking else 0,
                'contest_total_participated': contest_ranking.get('attendedContestsCount', 0) if contest_ranking else 0,
                'contest_top_percentage': contest_ranking.get('topPercentage', 100) if contest_ranking else 100,
                'recent_contests': recent_contests,
                'profile_url': f"https://leetcode.com/{username}/"
            }
            
        except requests.Timeout:
            return self.format_error('Request timed out. Please try again.')
        except Exception as e:
            return self.format_error(f'Error fetching LeetCode profile: {str(e)}')