import requests
from datetime import datetime
from bs4 import BeautifulSoup
from collections import Counter
import re

class ProfileAnalyzer:
    def __init__(self):
        self.cf_api = "https://codeforces.com/api"
        self.leetcode_api = "https://leetcode.com/graphql"
        self.codechef_api = "https://www.codechef.com/users"
        self.atcoder_api = "https://atcoder.jp/users"
        self.timeout = 10
        
    def get_codeforces_profile(self, handle):
        try:
            user_info = requests.get(f"{self.cf_api}/user.info?handles={handle}", timeout=self.timeout).json()
            submissions = requests.get(f"{self.cf_api}/user.status?handle={handle}", timeout=self.timeout).json()
            
            if user_info['status'] == 'OK':
                user_data = user_info['result'][0]
                submission_data = submissions.get('result', [])
                
                # Calculate verdict stats (AC, WA, etc.)
                verdicts = Counter(sub['verdict'] for sub in submission_data if 'verdict' in sub)
                ac_count = verdicts.get('OK', 0)
                
                # Calculate languages used
                languages = Counter(sub['programmingLanguage'] for sub in submission_data if 'programmingLanguage' in sub)
                top_languages = [f"{lang} ({count})" for lang, count in languages.most_common(3)]
                
                # Calculate problem tags
                tags = []
                for sub in submission_data:
                    if 'problem' in sub and 'tags' in sub['problem']:
                        tags.extend(sub['problem']['tags'])
                
                top_tags = [f"{tag} ({count})" for tag, count in Counter(tags).most_common(5)]
                
                # Calculate submission streak
                if submission_data:
                    submission_dates = sorted(set(datetime.fromtimestamp(sub['creationTimeSeconds']).strftime('%Y-%m-%d') 
                                             for sub in submission_data))
                    
                    current_streak = 1
                    max_streak = 1
                    for i in range(1, len(submission_dates)):
                        date1 = datetime.strptime(submission_dates[i-1], '%Y-%m-%d')
                        date2 = datetime.strptime(submission_dates[i], '%Y-%m-%d')
                        if (date2 - date1).days == 1:
                            current_streak += 1
                            max_streak = max(max_streak, current_streak)
                        else:
                            current_streak = 1
                
                return {
                    'handle': user_data['handle'],
                    'rating': user_data.get('rating', 'Unrated'),
                    'max_rating': user_data.get('maxRating', 'Unrated'),
                    'rank': user_data.get('rank', 'Unrated'),
                    'contributions': user_data.get('contribution', 0),
                    'submissions': len(submission_data),
                    'accepted_submissions': ac_count,
                    'acceptance_rate': f"{(ac_count / len(submission_data) * 100):.1f}%" if submission_data else "0%",
                    'top_languages': top_languages,
                    'favorite_tags': top_tags,
                    'max_streak': max_streak if submission_data else 0,
                    'registration_date': datetime.fromtimestamp(user_data['registrationTimeSeconds']).strftime('%Y-%m-%d'),
                    'last_online': datetime.fromtimestamp(user_data['lastOnlineTimeSeconds']).strftime('%Y-%m-%d')
                }
            return {'error': 'Unable to fetch Codeforces profile'}
        except requests.Timeout:
            return {'error': 'Request timed out. Please try again.'}
        except Exception as e:
            return {'error': f'Error fetching Codeforces profile: {str(e)}'}
            
    def get_leetcode_profile(self, username):
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            query = """
            {
                matchedUser(username: "%s") {
                    username
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
            }
            """ % username

            response = requests.post(
                self.leetcode_api,
                json={'query': query},
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return {'error': 'Unable to fetch LeetCode profile'}

            data = response.json()
            
            if 'errors' in data:
                return {'error': 'Invalid LeetCode username'}

            if data.get('data', {}).get('matchedUser') is None:
                return {'error': 'LeetCode user not found'}

            user_data = data['data']['matchedUser']
            submit_stats = user_data['submitStats']['acSubmissionNum']
            
            solved = {
                'total': 0,
                'easy': 0,
                'medium': 0,
                'hard': 0
            }
            
            for stat in submit_stats:
                if stat['difficulty'] == 'All':
                    solved['total'] = stat['count']
                elif stat['difficulty'] == 'Easy':
                    solved['easy'] = stat['count']
                elif stat['difficulty'] == 'Medium':
                    solved['medium'] = stat['count']
                elif stat['difficulty'] == 'Hard':
                    solved['hard'] = stat['count']

            return {
                'username': username,
                'total_solved': solved['total'],
                'easy_solved': solved['easy'],
                'medium_solved': solved['medium'],
                'hard_solved': solved['hard']
            }
            
        except requests.Timeout:
            return {'error': 'Request timed out. Please try again.'}
        except Exception as e:
            return {'error': f'Error fetching LeetCode profile: {str(e)}'}

    def get_codechef_profile(self, username):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(
                f"{self.codechef_api}/{username}",
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Rating
            rating = soup.find("div", class_="rating-number")
            rating = rating.text.strip() if rating else "Unrated"
            
            # Extract Division
            division_tag = soup.find("div", class_="rating-header")
            division = division_tag.find_all("div")[1].text.strip("()") if division_tag else "Unknown"
            
            # Extract Stars
            stars = len(soup.find_all("div", class_="rating-star"))
            
            # Extract Highest Rating
            highest_rating_tag = soup.find("small")
            highest_rating = highest_rating_tag.text.strip("()").split()[-1] if highest_rating_tag else "Unrated"
            
            # Extract Global Rank
            global_rank_tag = soup.find("a", href="/ratings/all")
            global_rank = global_rank_tag.find("strong").text.strip() if global_rank_tag else "Unranked"
            
            # Extract Country Rank
            country_rank_tag = soup.find("a", href=lambda x: x and "filterBy=Country" in x)
            country_rank = country_rank_tag.find("strong").text.strip() if country_rank_tag else "Unranked"
            
            # Get recent contests
            contest_history = []
            contest_table = soup.find('table', class_='rating-table')
            if contest_table:
                rows = contest_table.find_all('tr')[1:]  # Skip header
                for row in rows[:5]:  # Get last 5 contests
                    cols = row.find_all('td')
                    if len(cols) >= 3:  # Ensure we have enough columns
                        contest_name = cols[0].text.strip()
                        contest_date = cols[1].text.strip()
                        contest_rank = cols[2].text.strip()
                        if contest_name and contest_rank:
                            # Clean up the rank text
                            rank = ''.join(filter(str.isdigit, contest_rank))
                            contest_history.append({
                                'name': contest_name,
                                'date': contest_date,
                                'rank': f"#{rank}" if rank else 'Unranked'
                            })

            # Get solved problems count
            problems_solved = 0
            content_div = soup.find('div', class_='content')
            if content_div:
                problem_links = content_div.find_all('a')
                problems_solved = len(problem_links)

            return {
                'username': username,
                'rating': rating,
                'highest_rating': highest_rating,
                'division': division,
                'stars': f"{stars} ★" if stars > 0 else "0",
                'global_rank': f"#{global_rank}" if global_rank != 'Unranked' else global_rank,
                'country_rank': f"#{country_rank}" if country_rank != 'Unranked' else country_rank,
                'problems_solved': problems_solved,
                'recent_contests': [f"{contest['name']} ({contest['date']}): {contest['rank']}" 
                                for contest in contest_history] if contest_history 
                                else ['No recent contests'],
                'profile_url': f"https://www.codechef.com/users/{username}"
            }
            
        except requests.Timeout:
            return {'error': 'Request timed out. Please try again.'}
        except requests.exceptions.RequestException as e:
            return {'error': f'Failed to fetch details: {str(e)}'}
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}

    def get_atcoder_profile(self, username):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Get user profile
            profile_response = requests.get(
                f"{self.atcoder_api}/{username}",
                headers=headers,
                timeout=self.timeout
            )
            
            if profile_response.status_code != 200:
                return {'error': 'Invalid AtCoder username'}
                
            soup = BeautifulSoup(profile_response.text, 'html.parser')
            
            # Get table containing user stats
            table = soup.find('table', class_='dl-table')
            if not table:
                return {'error': 'Could not find user statistics'}
                
            stats = {}
            for tr in table.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    stats[th.text.strip()] = td.text.strip()
            
            # Extract rating and rank
            rating = stats.get('Rating', 'Unrated')
            if rating == '0':
                rating = 'Unrated'
                
            highest_rating = stats.get('Highest Rating', 'Unrated')
            if highest_rating == '0':
                highest_rating = 'Unrated'
                
            rank = stats.get('Rank', 'Unranked')
            if rank == '0':
                rank = 'Unranked'
                
            # Get solved count
            problems_solved = 0
            ac_count_span = soup.find('span', class_='user-ac-count')
            if ac_count_span:
                problems_solved = int(ac_count_span.text.strip())
                
            # Find the color class for the rating
            rating_color = "black"
            if soup.find('span', class_='user-gray'):
                rating_color = "gray"
            elif soup.find('span', class_='user-brown'):
                rating_color = "brown"
            elif soup.find('span', class_='user-green'):
                rating_color = "green"
            elif soup.find('span', class_='user-cyan'):
                rating_color = "cyan"
            elif soup.find('span', class_='user-blue'):
                rating_color = "blue"
            elif soup.find('span', class_='user-yellow'):
                rating_color = "yellow"
            elif soup.find('span', class_='user-orange'):
                rating_color = "orange"
            elif soup.find('span', class_='user-red'):
                rating_color = "red"
                
            # Get recent contests
            contests = []
            contest_table = soup.find('div', id='history')
            if contest_table:
                table_body = contest_table.find('tbody')
                if table_body:
                    rows = table_body.find_all('tr')
                    for row in rows[:5]:  # Get last 5 contests
                        cols = row.find_all('td')
                        if len(cols) >= 5:
                            contest_date = cols[0].text.strip()
                            contest_name = cols[1].text.strip()
                            contest_rank = cols[2].text.strip()
                            performance = cols[3].text.strip()
                            new_rating = cols[4].text.strip()
                            
                            contests.append({
                                'name': contest_name,
                                'date': contest_date,
                                'rank': contest_rank,
                                'performance': performance,
                                'new_rating': new_rating
                            })
            
            # Get language statistics
            lang_stats = {}
            submissions_page = requests.get(
                f"{self.atcoder_api}/{username}/history",
                headers=headers,
                timeout=self.timeout
            )
            
            if submissions_page.status_code == 200:
                subs_soup = BeautifulSoup(submissions_page.text, 'html.parser')
                submissions_table = subs_soup.find('table', class_='table')
                
                if submissions_table:
                    rows = submissions_table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 4:  # Make sure we have at least 4 columns
                            language = cols[3].text.strip()
                            if language:
                                lang_stats[language] = lang_stats.get(language, 0) + 1
            
            # Get top 3 languages
            top_languages = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)[:3]
            top_languages = [f"{lang} ({count})" for lang, count in top_languages]
            
            # Get additional information
            matches_participated = stats.get('Rated Matches', '0')
            rated_matches = int(matches_participated) if matches_participated.isdigit() else 0
            
            return {
                'username': username,
                'rating': rating,
                'rating_color': rating_color,
                'highest_rating': highest_rating,
                'rank': rank,
                'problems_solved': problems_solved,
                'rated_matches': rated_matches,
                'class': stats.get('Class', 'Unranked'),
                'recent_contests': [f"{c['name']} ({c['date']}): #{c['rank']} [Perf: {c['performance']}]" for c in contests],
                'top_languages': top_languages,
                'competitions': stats.get('Competitions', '0'),
                'birth_year': stats.get('Birth Year', 'Not specified'),
                'country': stats.get('Country/Region', 'Not specified')
            }
            
        except requests.Timeout:
            return {'error': 'Request timed out. Please try again.'}
        except Exception as e:
            return {'error': f'Error fetching AtCoder profile: {str(e)}'}