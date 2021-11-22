from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from levelupapi.models import Event, EventGamer, GameType, Game, Gamer

class EventTests(APITestCase):
    def setUp(self):
        """
        Create a new Gamer, collect the auth Token, and create a sample GameType
        """

        # Define the URL path for registering a Gamer
        url = '/register'

        # Define the Gamer properties
        gamer = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
            "bio": "Love those gamez!!"
        }

        # Initiate POST request and capture the response
        response = self.client.post(url, gamer, format='json')

        # Store the TOKEN from the response data
        self.token = Token.objects.get(pk=response.data['token'])

        # Use the TOKEN to authenticate the requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Assert that the response status code is 201 (CREATED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # SEED THE DATABASE WITH A GAMETYPE
        # This is necessary because the API does not
        # expose a /gametypes URL path for creating GameTypes

        # Create a new instance of GameType
        game_type = GameType()
        game_type.label = "Board game"

        # Save the GameType to the testing database
        game_type.save()
        
        url = "/games"

        # Define the Game properties
        game = {
            "title": "Clue",
            "maker": "Milton Bradley",
            "skillLevel": 5,
            "numberOfPlayers": 6,
            "gameTypeId": 1,
            "description": "More fun than a Barrel Of Monkeys!"
        }

        # Initiate POST request and capture the response
        response = self.client.post(url, game, format='json')

        # Assert that the response status code is 201 (CREATED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the values are correct
        self.assertEqual(response.data["gamer"]['user'], self.token.user_id)
        self.assertEqual(response.data["title"], game['title'])
        self.assertEqual(response.data["maker"], game['maker'])
        self.assertEqual(response.data["skill_level"], game['skillLevel'])
        self.assertEqual(response.data["number_of_players"], game['numberOfPlayers'])
        self.assertEqual(response.data["game_type"]['id'], game['gameTypeId'])
        
    def test_event_create(self):
        url = "/events"
        user = Gamer.objects.get(pk=1)
        event = {
            "gameId": 1,
            "description": "call Gus",
            "date": "2012-09-08",
            "time": "12:30:00"  
        }
        
        response = self.client.post(url, event, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
          
        self.assertEqual(response.data["game"]['id'], event['gameId'])
        self.assertEqual(response.data["description"], event["description"])
        self.assertEqual(response.data["date"], event["date"])
        self.assertEqual(response.data["time"], event["time"])
        self.assertEqual(response.data["organizer"]['id'], user.id)
        
    def test_get_single_event(self):
        user = Gamer.objects.get(pk=1)
        event = Event()
        event.organizer = user
        event.game = Game.objects.get(pk=1)
        event.date = "1223-09-22"
        event.time = "23:00:45"
        event.description = "don't call Gus"
        event.save()
        url = f'/events/{event.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["game"]['id'], event.game_id)
        self.assertEqual(response.data["description"], event.description)
        self.assertEqual(response.data["date"], event.date)
        self.assertEqual(response.data["time"], event.time)
        self.assertEqual(response.data["organizer"]['id'], event.organizer.id)
        
    def test_change_event(self):
        user = Gamer.objects.get(pk=1)
        event = Event()
        event.organizer = user
        event.game = Game.objects.get(pk=1)
        event.date = "1223-09-22"
        event.time = "23:00:45"
        event.description = "don't call Gus"
        event.save()
        url = f'/events/{event.id}'
        new_event = {
            "gameId": 1,
            "description": "mino Gus",
            "date": "2012-09-08",
            "time": "12:30:00"  
        }
        response = self.client.put(url, new_event, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data["game"]['id'], new_event['gameId'])
        self.assertEqual(response.data["description"], new_event["description"])
        self.assertEqual(response.data["date"], new_event["date"])
        self.assertEqual(response.data["time"], new_event["time"])
        self.assertEqual(response.data["organizer"]['id'], user.id)
        
    def test_delete_event(self):
        user = Gamer.objects.get(pk=1)
        event = Event()
        event.organizer = user
        event.game = Game.objects.get(pk=1)
        event.date = "1223-09-22"
        event.time = "23:00:45"
        event.description = "don't call Gus"
        event.save()
        url = f'/events/{event.id}'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
