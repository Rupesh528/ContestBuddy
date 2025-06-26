import requests
from datetime import datetime
from .base_analyzer import BaseProfileAnalyzer

class CodeforcesAnalyzer(BaseProfileAnalyzer):
    def __init__(self):
        super().__init__()
        self.api_base = "https://codeforces.com/api"
    
    def get_profile(self, handle):
        try:
            # Get user info
            user_info = requests.get(f"{self.api_base}/user.info?handles={handle}", timeout=self.timeout).json()
            if user_info['status'] != 'OK':
                return self.format_error('Unable to fetch Codeforces profile')
            
            user_data = user_info['result'][0]
            
            # Get submissions
            submissions_response = requests.get(f"{self.api_base}/user.status?handle={handle}", timeout=self.timeout).json()
            all_submissions = submissions_response.get('result', []) if submissions_response['status'] == 'OK' else []
            
            # Get contests
            contests_response = requests.get(f"{self.api_base}/user.rating?handle={handle}", timeout=self.timeout).json()
            contests = contests_response.get('result', []) if contests_response['status'] == 'OK' else []
            
            # Calculate problem statistics
            problems_solved = set()
            verdicts = {}
            languages = {}
            problem_ratings = {}
            
            for submission in all_submissions:
                verdict = submission.get('verdict', 'UNKNOWN')
                if verdict not in verdicts:
                    verdicts[verdict] = 0
                verdicts[verdict] += 1
                
                lang = submission.get('programmingLanguage', 'UNKNOWN')
                if lang not in languages:
                    languages[lang] = 0
                languages[lang] += 1
                
                if verdict == 'OK':
                    problem_id = (submission['problem']['contestId'], submission['problem']['index'])
                    problems_solved.add(problem_id)
                    
                    rating = submission['problem'].get('rating')
                    if rating:
                        if rating not in problem_ratings:
                            problem_ratings[rating] = 0
                        problem_ratings[rating] += 1
            
            # Get recent contests
            recent_contests = []
            for contest in contests[-5:]:  # Last 5 contests
                recent_contests.append({
                    'name': contest.get('contestName', 'Unknown'),
                    'rank': contest.get('rank', 'Unknown'),
                    'old_rating': contest.get('oldRating', 0),
                    'new_rating': contest.get('newRating', 0),
                    'date': datetime.fromtimestamp(contest['ratingUpdateTimeSeconds']).strftime('%Y-%m-%d')
                })
            
            # Format top languages
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Format problem difficulties
            difficulty_distribution = {}
            for rating, count in sorted(problem_ratings.items(), key=lambda x: x[0]):
                rating_range = f"{rating//100*100}-{rating//100*100+99}"
                if rating_range not in difficulty_distribution:
                    difficulty_distribution[rating_range] = 0
                difficulty_distribution[rating_range] += 1
            
            return {
                'handle': user_data['handle'],
                'rating': user_data.get('rating', 'Unrated'),
                'max_rating': user_data.get('maxRating', 'Unrated'),
                'rank': user_data.get('rank', 'Unrated'),
                'contribution': user_data.get('contribution', 0),
                'friend_of_count': user_data.get('friendOfCount', 0),
                'total_submissions': len(all_submissions),
                'problems_solved': len(problems_solved),
                'accepted_submissions': verdicts.get('OK', 0),
                'wrong_submissions': verdicts.get('WRONG_ANSWER', 0),
                'contests_participated': len(contests),
                'last_online': datetime.fromtimestamp(user_data['lastOnlineTimeSeconds']).strftime('%Y-%m-%d'),
                'registered_date': datetime.fromtimestamp(user_data['registrationTimeSeconds']).strftime('%Y-%m-%d'),
                'top_languages': [f"{lang} ({count})" for lang, count in top_languages],
                'problem_ratings': difficulty_distribution,
                'recent_contests': recent_contests,
                'profile_picture': user_data.get('titlePhoto', 'https://codeforces.com/predownloaded/no-avatar.jpg')
            }
        except requests.Timeout:
            return self.format_error('Request timed out. Please try again.')
        except Exception as e:
            return self.format_error(f'Error fetching Codeforces profile: {str(e)}')

