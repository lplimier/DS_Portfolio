from time import sleep
from os import system, name
from random import randrange

from egg import cracking_egg

class Pastry_Chef():
    """Represents the main player in the game, the Pastry Chef.
        Takes a name and stores attributes that will be modified as the player moves through the game."""
    def __init__(self,name):
        self.name = name
        self.chef_rank = "Apprentice Chef"
        self.chef_points = 0
        self.order_points = 0
        self.location = ""
        self.inventory = []
        self.pan_inventory = []
        self.order_count = 0
        self.delivery_count = 0 
        self.easter_egg = 1

    def clear_screen():
        """ This simple function comes from here: https://www.geeksforgeeks.org/clear-screen-python/. 
            It works perfectly on my Windows command line. I don't have a Mac to test whether it works there.
            It does not work at the git bash prompt."""
        if name == "nt":
            clear = system('cls')
        else:
            clear = system('clear')

    def update_rank(self):
        """Modifies the rank of the pastry_chef based on number of points.
            Returns the player's rank."""
        if self.chef_points <= 100:
            self.chef_rank = "Apprentice Chef"
        elif self.chef_points > 100 and self.chef_points <= 200:
            self.chef_rank = "Novice Chef"
        elif self.chef_points > 200 and self.chef_points <= 300:
            self.chef_rank = "Advanced Chef"
        elif self.chef_points > 300:
            self.chef_rank = "Master Chef"

        return self.chef_rank 
    
    def get_item(self,area,item_list):
        """Takes a list of inventory items from an area in a room. Prints the list for the user to choose.
        Adds chosen items from the area's inventory to the chef's personal inventory."""
        potential_choices = []
        print("-"*80,"\nYou have just opened the {}.\nThe {} has the following items:\n".format(area,area),"-"*80)
        v = 1
        while v:
            for i in range(0,len(item_list)):
                print("    [{}] {}.".format((i + 1),item_list[i]))
                potential_choices += [str(i + 1)]
            print("    [{}] Nothing. Close the {}.\n".format((len(item_list) + 1),area),"-"*80)
            potential_choices += [str(len(item_list) + 1)]
            # Simple error handling.
            w = 1
            while w:
                choice = input("What would you like to take from the {}?".format(area))
                if choice not in potential_choices:
                    print("You must choose a number between 1 and {}.".format(len(item_list) + 1))
                else:
                    w = 0
                    Pastry_Chef.clear_screen()
                    print("-"*80)
            if int(choice) != (len(item_list) + 1):
                # Add the chosen item to the chef's inventory of pans.
                if area == "Counter Storage":
                    x = item_list[int(choice)-1].split(" (")
                    self.pan_inventory += [x[0]]
                else:
                    self.inventory += [item_list[int(choice)-1]]
                print("You have just taken {} from the {}.\n".format(item_list[int(choice)-1],area),"-"*80)
                enter = input("Press 'Enter' to continue.")
                Pastry_Chef.clear_screen()
                # Hrm... too many eggs...
                if self.inventory.count("eggs") == 6 and self.easter_egg:
                    print("You have 6 eggs in your inventory.\nIt's six of one and half a dozen of another.\nBut either way, it's worth celebrating!")
                    cracking_egg()
                    self.easter_egg = 0
                    print("Lucky you... Chef {}, you just earned a bonus half-a-dozen points!\n".format(self.name),"-"*80)
                    self.chef_points += 6
                    enter = input("Press 'Enter' to continue.")
                    Pastry_Chef.clear_screen()	
            else:
                v = 0
        print("You have just closed the {}\n".format(area),"-"*80)
                                
    def __str__(self):
        return "{}".format(self.name)

class Room():
    """Represents a location within the game. The player's choices vary depending on the room,
        but the functions are defined in this parent class."""
    def enter_room(self, chef):
        print("Chef {}, you are in the {}.".format(chef, self))
        print("-"*80)
        enter = input("Press 'Enter' to continue.")
        # Call the choose_next_action function to 
        self.choice = self.choose_next_action(self.action_choices)
        return self.choice

    def choose_next_action(self, action_choices):
        """Takes a list of possible choices for the next action,
            prints the choices for the player,
            and returns the action choice as a string."""
        potential_choices = []
        print("From the {} you can:".format(self))
        self.action_choices = action_choices
        for i in range(0,len(self.action_choices)):
            print("    [{}] {}.".format((i + 1),self.action_choices[i]))
            potential_choices += [str(i + 1)]
        # Simple error handling.
        w = 1
        while w:
            choice = input("What would you like to do?")
            if choice not in potential_choices:
                print("You must choose a number between 1 and {}.".format(len(self.action_choices)))
            else:
                w = 0
        Pastry_Chef.clear_screen()
        self.action = self.action_choices[(int(choice) - 1)]
        return self.action
    
    def choose_next_room(self,room,room_choices):
        """Takes a list of possible choices for the next room,
            displays them for the player and returns the chosen location."""
        potential_choices = []
        print("From the {} you can:".format(room))
        for i in range(0,len(room_choices)):
            print("    [{}] Enter the {}.".format((i + 1),room_choices[i]))
            potential_choices += [str(i + 1)]
        # Simple error handling.
        w = 1
        while w:
            choice = input("What would you like to do?")
            if choice not in potential_choices:
                print("You must choose a number between 1 and {}.".format(len(self.action_choices)))
            else:
                w = 0
        Pastry_Chef.clear_screen()
        self.location = room_choices[(int(choice) - 1)]
        return self.location
        
class Lobby(Room):
    """The entry room for the game. From here the player can either quit the game
        or start the game by entering any other room."""      
    
    def __init__(self, chef):
        """Defines the choices for other rooms and the actions the player can take from the Lobby"""
        self.lobby_start = "Enter {}'s Bakery and start playing".format(chef)
        self.lobby_resume = "Enter {}'s Bakery and resume playing".format(chef)
        self.room_choices = ["Storefront", "Office", "Kitchen"]
        self.action_choices = [self.lobby_start, "Quit"]
        self.resume_action_choices = [self.lobby_resume, "Quit"]

    def __str__(self):
        return "Lobby"
    def __repr__(self):
        return self.__str__()

class Storefront(Room):
    """Represents the storefront where you can take orders from customers
        and deliver completed orders to customers."""
    def __init__(self, chef):
        """Defines the choices for other rooms and the actions the player can take from the Storefront"""
        self.room_choices = ["Office", "Kitchen"]
        self.action_choices = ["Enter a different room","Take a customer's order","Deliver an order to a customer", "Return to the Lobby to exit the game"]
    def __str__(self):
        return "Storefront"
    
class Office(Room):
    """Represents the office where you can take orders over the phone or via email."""
    def __init__(self, chef):
        """Defines the choices for other rooms and the actions the player can take from the Office"""
        self.room_choices = ["Storefront", "Kitchen"]
        self.action_choices = ["Enter a different room","Check your e-mail","Answer the phone", "Return to the Lobby to exit the game"]
    def __str__(self):
        return "Office"
    
class Kitchen(Room):
    """Represents the kitchen where you can prepare desserts."""
    def __init__(self, chef):
        """Defines the choices for other rooms and the actions the player can take from the Kitchen"""
        self.room_choices = ["Office", "Storefront"]
        self.action_choices = ["Enter a different room","Go to the pantry","Bake something in the oven","Go to the counter", "Go to the refrigerator", "Help! Remind me what's in my inventory", "Help! Remind me what my customer ordered", "Return to the Lobby to exit the game"]
    def __str__(self):
        return "Kitchen"
    
class Area(Room):
    """This is a shell class for areas within rooms that the player can interact with.
    I used the "Room" parent class because the functionality is basically the same as a room."""
    def __init__(self):
        pass
    
class Pantry(Area):
    """Stores the room temperature ingredients for the desserts."""
    def __init__(self):
        self.pantry_inventory = ["flour, sugar, levening, salt","vanilla extract",
                                 "cinnamon, nutmeg, cloves","cocoa powder",
                                 "confectioners sugar","vegetable oil"]
    
    def interact_in_area(self,chef,area):
        self.chef = chef
        self.area = area
        self.chef.get_item(self.area,self.pantry_inventory)
                  
    def __str__(self):
        return "Pantry"
    
class Fridge(Area):
    """Stores the refrigerated ingredients for the desserts."""
    def __init__(self):
        self.fridge_inventory = ["eggs","milk","butter","lemons","caramel sauce"]
    
    def interact_in_area(self,chef,area):
        self.chef = chef
        self.area = area
        self.chef.get_item(self.area,self.fridge_inventory)
                  
    def __str__(self):
        return "Refrigerator"

class Counter(Area):
    """Stores pans/bowl and allows the player to mix and frost cakes."""

    def __init__(self):
        self.serving_size_dict = {'6" round pans':8,'8" round pans':14,'10" round pans':25,
                                  'quarter sheet pan':30,'half sheet pan':60,'10" square pans':30}
        self.counter_inventory = ['6" round pans (serves 8 people)','8" round pans (serves 14 people)',
                                  '10" round pans (serves 25 people)','quarter sheet pan (serves 30 people)',
                                  'half sheet pan (serves 60 people)','10" square pans (serves 30 people)']
        self.flavor_dict = {"vanilla":"vanilla extract","spice":"cinnamon, nutmeg, cloves",
                            "chocolate":"cocoa powder","lemon":"lemons","caramel":"caramel sauce"}
    
    def interact_in_area(self,chef,area):
        self.chef = chef
        self.area = area
        self.action_choices = ["Get pans to bake your cake","Mix the cake batter",
                               "Mix the frosting","Frost the cake","Leave the counter"]
        choice = self.choose_next_action(self.action_choices)
        if choice == "Leave the counter":
            return
        elif self.chef.has_order == 0:
            print("Ooops! You need an order before you can make a cake. \nYou just lost 5 points.\
                  \n[Hint: get new orders from the Office or the Storefront.]\n","-"*80)
        elif choice == "Get pans to bake your cake":
            self.chef.get_item("Counter Storage",self.counter_inventory)
            # Check to see if the chef got the correct size and shape pan from the counter storage area.
            for i in self.chef.pan_inventory:
                if "round" in i and "round" in self.chef.order:
                    if self.serving_size_dict[i] >= self.chef.order[4]:
                        self.chef.cake.has_pan = 1
                        self.chef.cake.pan = i
                        break
                if "square" in i and "square" in self.chef.order:
                    if self.serving_size_dict[i] >= self.chef.order[4]:
                        self.chef.cake.has_pan = 1
                        self.chef.cake.pan = i
                        break
                if "sheet" in i and "sheet" in self.chef.order:
                    if self.serving_size_dict[i] >= self.chef.order[4]:
                        self.chef.cake.has_pan = 1
                        self.chef.cake.pan = i
                        break
        elif choice == "Mix the cake batter":
            flavor_ingredient = [self.flavor_dict[self.chef.cake.flavor]]
            cake_ingredients = ["flour, sugar, levening, salt","vegetable oil","eggs","milk"] + flavor_ingredient
            # Check to see if the chef has all the ingredients to mix the cake.
            if set(cake_ingredients) <= set(self.chef.inventory):
                self.chef.cake.is_mixed = 1
                print("You just mixed your cake batter.\n","-"*80)
                # Remove the used ingredients from the chef's inventory.
                for c in cake_ingredients:
                    self.chef.inventory.remove(c)
            else:
                self.chef.order_points -= 5
                print("Ooops! You don't have the right ingredients to mix your batter.\nYou just lost 5 points.\
                    \n[Hint: you need flour mix, oil, flavoring, eggs and milk.]\n,","-"*80)
        elif choice == "Mix the frosting":
            flavor_ingredient = [self.flavor_dict[self.chef.cake.frosting_flavor]]
            frosting_ingredients = ["confectioners sugar","butter"] + flavor_ingredient
            # Check to see if the chef has all the ingredients to mix the frosting.
            if set(frosting_ingredients) <= set(self.chef.inventory):
                self.chef.cake.has_frosting = 1
                print("You just mixed your frosting.\n","-"*80)
                for c in frosting_ingredients:
                # Remove the used ingredients from the chef's inventory.
                    self.chef.inventory.remove(c)
            else:
                self.chef.order_points -= 5
                print("Ooops! You don't have the right ingredients to mix your frosting.\nYou just lost 5 points.\
                    \n[Hint: you need confectioners sugar, butter and flavoring.]\n","-"*80)
        elif choice == "Frost the cake":
            if self.chef.cake.has_frosting and self.chef.cake.is_baked and not self.chef.cake.is_frosted:
                print("You just frosted your cake.\n","-"*80)
                self.chef.cake.is_frosted = 1
            else:
                self.chef.order_points -= 5
                print("Ooops! You couldn't frost your cake.\nYou just lost 5 points.\
                    \n[Hint: you need to have mixed frosting and a baked, unfrosted cake.]\n","-"*80)
        enter = input("Press 'Enter' to continue.")
        Pastry_Chef.clear_screen()
        self.interact_in_area(self.chef,self.area)
                  
    def __str__(self):
        return "Counter"
    
class Oven(Area):
    """Changes the status of a mixed dessert into a baked dessert."""
    def __init__(self):
        pass
    def interact_in_area(self,chef,area):
        self.chef = chef
        self.area = area
        if self.chef.has_order == 0:
            print("Ooops! You need an order before you can bake a cake. \nYou just lost 5 points.\
                  \n[Hint: get new orders from the Office or the Storefront.]\n","-"*80)
        elif self.chef.cake.is_mixed and not self.chef.cake.is_baked:
            if self.chef.cake.has_pan:
                print("You just baked your cake. Good work!")
                print("-"*80)
                self.chef.cake.is_baked = 1
                # Remove the used pan from the chef's inventory.
                self.chef.pan_inventory.remove(self.chef.cake.pan)
            else:
                self.chef.order_points -= 5
                print("Ooops! You don't have the correct pan to bake this cake.\nYou just lost 5 points.\
                      \n[Hint: you must have a pan of the right size and shape for your order.]\n","-"*80)

        else:
            self.chef.order_points -= 5
            print("Ooops! You don't have anything ready to bake in the oven.\nYou just lost 5 points.\
                  \n[Hint: you must have a pan with mixed batter in order to bake a cake.]\n","-"*80)
        enter = input("Press 'Enter' to continue.")
        Pastry_Chef.clear_screen()
    
class Computer(Area):
    """Represents email, which may contain a customer order or may be spam."""

    def interact_in_area(self,chef,area):
        self.chef = chef
        self.area = area
        email_order = randrange(0,4)
        print("Chef {}, you've got mail! Let's open it.".format(self.chef))
        enter = input("Press 'Enter' to continue.")
        Pastry_Chef.clear_screen()
        # There is a 75% chance of getting an email order.
        if email_order > 0:
            print("It looks like you got an order request from a customer.\n","-"*80)
            enter = input("Press 'Enter' to continue.")
            Pastry_Chef.clear_screen()
            self.chef.customer = Customer()
            self.chef.customer.get_order(self.chef)
        else:
            print("You have nothing but spam messages in your email.\nAnd a note from {}sMom1965@chefmail.com.\
                  \nIs that your mom? She says she misses you.\n".format(str(chef).replace(" ","")),"-"*80)
            enter = input("Press 'Enter' to continue.")
            Pastry_Chef.clear_screen()
class Phone(Area):
    """Represents customers on the phone who may have an order or may just want directions."""

    def interact_in_area(self,chef,area):
        self.chef = chef
        self.area = area
        phone_order = randrange(0,4)
        print("Chef {}, your phone is ringing! Let's answer it.".format(self.chef))
        enter = input("Press 'Enter' to continue.")
        Pastry_Chef.clear_screen()
        # There is a 75% chance of getting a phone order.
        if phone_order > 0:
            print("A customer called you to place an order.")
            enter = input("Press 'Enter' to continue.")
            Pastry_Chef.clear_screen()
            self.chef.customer = Customer()
            self.chef.customer.get_order(self.chef)
        else:
            print("Your customer just wanted directions to your bakery.\nHe must not have a smartphone.\
                  \nOr smart anything really.\n","-"*80)
            enter = input("Press 'Enter' to continue.")
            Pastry_Chef.clear_screen()

class Customer():
    """This is a euphemism for getting and delivering orders, since there are no customer NPC's in this game."""
    def __init__(self):
        self.order_points = 0
        
    def generate_order(self):
        """Creates a list that randomly selects flavors, shape and size of the cake. Returns the list."""
        cake_flavors = ["chocolate", "vanilla", "spice", "lemon"]
        frosting_flavors = ["vanilla", "chocolate", "caramel", "lemon"]
        cake_shapes = ["round","square","sheet"]
        # Each tuple value is the range of the number of people the cake could feed.
        cake_sizes = {"round":(6,26),"square":(15,31),"sheet":(15,61)}
        # Randomly chooses one of the cake flavors, shapes and frosting flavors.
        random_order = ["cake",cake_flavors[randrange(0,4)],frosting_flavors[randrange(0,4)],
                        cake_shapes[randrange(0,3)]]
        # Uses the cake size tuple to randomly choose a number of people within that range.
        random_size = randrange(cake_sizes[random_order[3]][0],cake_sizes[random_order[3]][1])
        random_order += [random_size]
        return random_order
    
    def get_order(self,chef):
        """Gets an order from a customer. """
        self.chef = chef
        if self.chef.order_count == 0:
            print("Congratulations Chef {}!! You have just received your first order!".format(self.chef))
        else:
            w = 1
            while self.chef.has_order and w:
                print("You already have an open order. Do you want to replace it with a new order?")
                replace = input("Enter 'Y' for Yes or 'N' for No. ")
                if replace == "Y" or replace == "y":
                    self.chef.order_points = 0
                    w = 0
                elif replace == "N" or replace == "n":
                    Pastry_Chef.clear_screen()
                    return
            print("You have just received an order.")
        self.chef.has_order = 1
        self.chef.order_count += 1
        self.chef.order_points += 75
        self.chef.order = self.generate_order()
        print("\n","*"*80,"\nYour customer ordered a {}, {} {} with {} frosting for {} people.\n"\
              .format(self.chef.order[1],self.chef.order[3],self.chef.order[0],self.chef.order[2],self.chef.order[4]),"*"*80)
        self.chef.cake = Cake(self.chef.order[1:])        
        enter = input("Press 'Enter' to continue.")
        Pastry_Chef.clear_screen()
        return
    
    def deliver_order(self,chef,cake):
        """Delivers a completed order to a customer."""
        self.chef = chef
        self.chef.cake = cake
        if self.chef.cake.is_frosted and self.chef.has_order:
            self.chef.chef_points += self.chef.order_points
            self.chef.delivery_count += 1
            self.chef.has_order = 0
            rank = self.chef.update_rank()
            print("You just delivered an order.\n","-"*80)
            if self.chef.order_points == 75:
                print("Good work, Chef {}! You made no errors in completing that order.\n You earned 10 bonus points!".format(self.chef))
                self.chef.chef_points += 10
                enter = input("Press 'Enter' to continue.")
                Pastry_Chef.clear_screen()
            print("Congratulations Chef {}, you just earned {} points for delivering your order!\nYour rank is {} and your score is {}."\
                 .format(self.chef,self.chef.order_points,rank,self.chef.chef_points))
            self.chef.order_points = 0
        else:
            self.chef.order_points -= 5
            print("Ooops! You don't have a finished cake to deliver.\nYou just lost 5 points.\
            \n[Hint: You must go to the kitchen to make a cake. You can't deliver a cake until it's mixed, baked and frosted.]\n","-"*80)
        enter = input("Press 'Enter' to continue.")
        Pastry_Chef.clear_screen()
        return

class Dessert():
    """Represents dessert items to be baked by the pastry chef. 
    Having this parent class allows me to add other desserts, like cookies,
    which I was originally planning to do."""
    def __init__(self):
        pass
        
class Cake(Dessert):
    """Represents a cake dessert through all its iterations (ordered, mixed, baked, decorated, delivered)"""
    def __init__(self, order):
        self.flavor = order[0]
        self.frosting_flavor = order[1]
        self.shape = order[2]        
        self.size = order[3]
        self.is_mixed = 0
        self.is_baked = 0
        self.is_frosted = 0
        self.is_delivered = 0
        self.has_frosting = 0
        self.has_pan = 0
        self.pan = ""
        
class Pastry_Game():
    """Houses the backbone of the game."""
    def __init__(self, chef):
        """Takes a Player and initializes the game."""
        self.chef = chef
        # Initialize rooms.
        self.Lobby = Lobby(self.chef)
        self.Storefront = Storefront(self.chef)
        self.Office = Office(self.chef)
        self.Kitchen = Kitchen(self.chef)
        # Initialize areas.
        self.pantry = Pantry()
        self.oven = Oven()
        self.fridge = Fridge()
        self.computer = Computer()
        self.phone = Phone()
        self.counter = Counter()
        # Initialize the rooms, so locations can be passed as other than strings.
        self.room_dict = {"Lobby": self.Lobby, "Storefront": self.Storefront, "Office": self.Office,
                          "Kitchen": self.Kitchen}
        # Contains all the actions in the game.
        self.action_dict = {"Quit": 0, "Enter a different room":1, "Return to the Lobby to exit the game":9,
                            "Go to the pantry":self.pantry, "Bake something in the oven":self.oven,"Go to the counter":self.counter,
                            "Go to the refrigerator":self.fridge, "Check your e-mail":self.computer,
                            "Answer the phone":self.phone, "Take a customer's order":7,
                            "Deliver an order to a customer":8, self.Lobby.lobby_resume:1,
                            "Help! Remind me what's in my inventory":2, "Help! Remind me what my customer ordered":3}

        self.play_game(self.chef)
        
    def play_game(self,chef):
        """Plays the game by moving the player through rooms and giving the player choices."""
        self.chef = chef
        self.chef.has_order = 0
        Pastry_Chef.clear_screen()
        if self.Lobby.enter_room(self.chef) != "Quit":
            Pastry_Chef.clear_screen()
            # Display a pretty and useful message to introduce the game to the player. This only happens once.
            print("Welcome to {}'s Bakery!".format(chef))
            print("Your job is to:\n    ** Take orders for tasty treats.\n    ** Mix, bake and decorate those treats.\n    ** Deliver them to your customers.")
            enter = input("Press 'Enter' to continue.")
            Pastry_Chef.clear_screen()
            print("It's a new day and it's time to take some orders and do some baking.\n","-"*80)
            print("              .-~~~-.\n            (` '` `' `)\n          (` '` '`' `' `)\n         (`' `' `'` '` '`)\n          ~\\|||||||||||/~\n            \\|||||||||/\n             \|||||||/\n","-"*80)
            enter = input("Press 'Enter' to continue.")
            Pastry_Chef.clear_screen()
            # Call the choose_next_room function to display the initial room choices to the player.
            self.chef.location = self.Lobby.choose_next_room(self.Lobby,self.Lobby.room_choices)
            # Will give a choice of "resume playing" instead of "start playing" the next time the player enters the lobby.
            self.Lobby.action_choices = self.Lobby.resume_action_choices
            # Call the enter_room function to display action choices for the chosen room.
            choice = self.room_dict[self.chef.location].enter_room(self.chef)
            # Keep playing the game as long as the player doesn't want to quit.
            while self.action_dict[choice] != 0:
                if self.action_dict[choice] == 1:
                    # Call the choose_next_room function to display room choices to the player.
                    self.chef.location = self.room_dict[self.chef.location].\
                                         choose_next_room(self.room_dict[self.chef.location],\
                                         self.room_dict[self.chef.location].room_choices)
                    # Call the enter_room function to display action choices for the chosen room.
                    choice = self.room_dict[self.chef.location].enter_room(self.chef)
                # Give the player the option to quit or resume playing.
                elif self.action_dict[choice] == 9:
                    self.chef.location = "Lobby"
                    choice = self.room_dict[self.chef.location].choose_next_action(self.room_dict[self.chef.location].resume_action_choices)
                # The player chose to get an order from a customer.
                elif self.action_dict[choice] == 7:
                    #Use random generator to give 75% chance of having customer in the Bakery.
                    customer_in_storefront = randrange(0,4)
                    if customer_in_storefront > 0:
                        print("There's a customer in {}'s Bakery! Let's take an order.".format(self.chef))
                        enter = input("Press 'Enter' to continue.")
                        Pastry_Chef.clear_screen()
                        self.chef.customer = Customer()
                        self.chef.customer.get_order(self.chef)
                    else:
                        print("There's no customer in {}'s Bakery right now.\nYou did remember to unlock the door this morning, didn't you?".format(self.chef))
                        enter = input("Press 'Enter' to continue.")
                        for i in range(0,5):
                            # This sleep function does not work for me at the git bash prompt. (Works perfectly at Windows command line.)
                            sleep(1)
                            print("...")
                        print("Didn't you?")
                        sleep(2)
                        input("Nevermind. I'm sure you unlocked the door.\nI guess it's just a slow day for business.\n Press 'Enter' to continue.")
                    Pastry_Chef.clear_screen()
                    choice = self.room_dict[self.chef.location].enter_room(self.chef)
                # The player chose to deliver an order to the customer.
                elif self.action_dict[choice] == 8:
                    if self.chef.has_order == 0:
                        print("Ooops! You haven't taken an order.\
						    \nYou must take an order before you can deliver an order.\n","-"*80)
                        enter = input("Press 'Enter' to continue.")
                        Pastry_Chef.clear_screen()
                    else:
                        self.chef.customer.deliver_order(self.chef,self.chef.cake)
                    choice = self.room_dict[self.chef.location].enter_room(self.chef)
                # The player chose to look at the chef's inventory.
                elif self.action_dict[choice] == 2:
                    print("So, you can't remember what items you have?\nA little early onset dementia maybe?")
                    sleep(2)
                    print("I'm happy to tell you what you have in your inventory, but it'll cost you 5 points.")
                    sleep(2)
                    print("-"*80,"\nDo you still want help?\n")
                    help_me = input("If so, enter 'Y' for yes.")
                    Pastry_Chef.clear_screen()
                    if help_me == "Y" or help_me == "y":
                        print("Well, you'll never make it to Master Chef\nif you keep throwing your points away like that!")
                        if len(self.chef.inventory) > 0 or len(self.chef.pan_inventory) > 0:
                            print("Here is your current inventory:")
                            for i in self.chef.inventory:
                                print("    **",i)
                            for i in self.chef.pan_inventory:
                                print("    **",i)
                        else:
                            print("Looks like your inventory is empty. Sure is a bummer to lose those points!")
                        self.chef.order_points -= 5
                    else:
                        print("Good choice.\nYou gotta save up your points if you ever want to make it to Master Chef!")
                    input("Press 'Enter' to continue")
                    Pastry_Chef.clear_screen()
                    choice = self.room_dict[self.chef.location].enter_room(self.chef)
                # The player chose to look at the current order.
                elif self.action_dict[choice] == 3:
                    if self.chef.has_order:
                        print("So, you can't remember what your customer ordered, huh?\nDid you forget to write it down?")
                        sleep(2)
                        print("You know, on one of those little order pads you bought\nwith the cute little cupcake logo on it.")
                        sleep(2)
                        print("              .-~~~-.\n            (` '` `' `)\n          (` '` '`' `' `)\n         (`' `' `'` '` '`)\n          ~\\|||||||||||/~\n            \\|||||||||/\n             \|||||||/\n","-"*80)
                        print("Well, no. Not that logo. But close enough.")
                        sleep(2)
                        input("Press 'Enter' to continue")
                        Pastry_Chef.clear_screen()
                        print("Okay, I'll tell you what your customer ordered, but it'll cost you 5 points.")
                        sleep(2)
                        print("Do you still want help?\n","-"*80)
                        help_me = input("If so, enter 'Y' for yes.")
                        Pastry_Chef.clear_screen()
                        if help_me == "Y" or help_me == "y":
                            print("I'll tell ya, you're never gonna make it to Master Chef\nif you keep throwing your points away like that!")
                            input("Press 'Enter' to continue")
                            print("*"*80,"\nYour customer ordered a {}, {} {} with {} frosting for {} people.\n"\
                                  .format(self.chef.order[1],self.chef.order[3],self.chef.order[0],self.chef.order[2],self.chef.order[4]),"*"*80)
                            self.chef.order_points -= 5
                        else:
                            print("Good choice.\nYou gotta save up your points if you ever want to make it to Master Chef!")
                    else:
                        print("Looks like you don't have a customer order right now.")
                    input("Press 'Enter' to continue")
                    Pastry_Chef.clear_screen()
                    choice = self.room_dict[self.chef.location].enter_room(self.chef)
                else:
                    # Call the interact_in_area function to display what the player can do in the current area.
                    self.action_dict[choice].interact_in_area(self.chef,self.action_dict[choice])
                    # Call the enter_room function to display action choices for the current room.
                    choice = self.room_dict[self.chef.location].enter_room(self.chef)

            print("Goodbye Chef {}. Thanks for playing!\nYou made it to rank of {} with {} points!".format(self.chef,self.chef.chef_rank,self.chef.chef_points))
            sleep(5)
            return
        else:
            print("Goodbye Chef {}. Thanks for playing!\nYou made it to rank of {} with {} points!".format(self.chef,self.chef.chef_rank,self.chef.chef_points))
            sleep(5)
            return

x = input("This is PASTRY CHEF. The epic game of baking delicious cakes.\nGrab your apron and your oven mitts... it's about to get hot in the kitchen!\n\nPlease enter a name for your chef:")
player = Pastry_Chef(x)
play = Pastry_Game(player)
