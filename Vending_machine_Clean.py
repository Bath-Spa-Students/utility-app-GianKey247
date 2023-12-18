import json
import glob
data={}

#Preloads the data from the 'item_Data' folder for optimization purposes
def preload_data():
        #Takes all files in the folder
    for file_json in glob.glob("Item_Data" + "/*"):
        index=0
        # load a json file 
        with open(file_json, "r") as json_file:
            json_data=json.load(json_file)
            item_Type = json_data["Item_Type"]
        # prints all items within the json
        for item_Data in json_data["Items"]:
            index = index + 1
            item_Code_Letter = item_Type[0]
            item_Code_Number = index
            item_Code = f"{item_Code_Letter}{item_Code_Number}"
            item_Data.update({"Item_Type":item_Type})
            data.update({item_Code:item_Data})

#Prints out a menu using 'Item_Name' from the json files
#Designates a item code for each menu item using the first letter of 'Item_Type' and a index
def printMenu():
    item_Type = ""
    index=0
    for item_Data in data.values():
        if item_Type != item_Data["Item_Type"]:
            item_Type = item_Data["Item_Type"]
            index=0
            print(f"---------------------{item_Type}---------------------")
        index = index + 1
        item_Stock = item_Data["Item_Stock"]
        item_Code_Letter = item_Type[0]
        item_Code_Number = index
        item_Code = f"{item_Code_Letter}{item_Code_Number}"
        item_Name = item_Data["Item_Name"]
        item_Price = item_Data["Item_Price"]
        print(f'[{item_Code}]{item_Name}\tPrice:{item_Price}\t\tStock:{item_Stock}')


def get_json_data(item_Type):
    with open("Item_Data" + f"/{item_Type}.json", "r") as json_file:
        json_data=json.load(json_file)
    return json_data


# chosen_items={"B1":2, "B3": 3}
chosen_items={}

#manages the whole of the users input and interaction    
def manageUserInput():
    global Money
    item_Data ,Users_Item= get_User_Item_Code()
    item_Name = item_Data['Item_Name']
    Users_Confirmation = get_User_Confirmation(f"Are you sure you want to buy {item_Name} (Y/N):")


    if Users_Confirmation.upper() == "Y":
        Users_Item_Quantity = get_Users_Item_Quanitiy(item_Name)

        if chosen_items.get(Users_Item) is not None:
            Users_Item_Quantity = Users_Item_Quantity + chosen_items[Users_Item]
        while not is_stock_enough(Users_Item, Users_Item_Quantity) or item_Data['Item_Stock'] < 0:
            print(f"You bought {Users_Item_Quantity} of {item_Name}")
            print(f"The vending machine only have {item_Data['Item_Stock']}")
            Users_Item_Quantity = get_Users_Item_Quanitiy(item_Name)
            

        print(f"{Users_Item_Quantity} of {item_Name} is added to checkout")
        chosen_items.update({Users_Item:Users_Item_Quantity})
        total_cost = Total_Cost(chosen_items)
        
        while total_cost > Money:
            print(f"You dont have enough money to pay for your items which is {total_cost}")
            Money = Money + int(input("Insert more money: "))
            #Money=Money+20
            print(f"Now your balance is {Money}")
        
        Users_Confirmation = get_User_Confirmation("Would you like to buy more items (Y/N): ")

        if Users_Confirmation.upper()=="Y":
            give_recommendation()
        elif Users_Confirmation.upper() == "N":
            #print(f"You baught 1 {item_Name} and it will cost {item_Data['Item_Price']}")
            Checkout(chosen_items)

    elif Users_Confirmation.upper() == "N":
        manageUserInput()

#retieves the item data by using the item code
#returns items data and users_item_code
def get_User_Item_Code():
    Users_Item = input("Enter Item code (Example: B1 for Fita): ")
    while Users_Item not in data.keys():
        print(f"your input is invalid")
        Users_Item = input("Enter Item code (Example: B1 for Fita): ")
    item_Data = getItemData(Users_Item)
    return item_Data, Users_Item

#asks the user for confirmation of action
#returns Users_Confirmation
def get_User_Confirmation(input_message):
    Users_Confirmation = input(input_message)
    while Users_Confirmation.upper() != "Y" and Users_Confirmation.upper() != "N":
        print("Your input on Users Confirmation is invalid")
        Users_Confirmation = input(input_message)
    return Users_Confirmation

#asks the user for quantity of item selected
#returns Users_Item_Quantity
def get_Users_Item_Quanitiy(item_Name):
        Users_Item_Quantity = int(input(f"How many of this {item_Name} would you like: "))
        while Users_Item_Quantity<0:
            print(f"your input is invalid")
            Users_Item_Quantity = int(input(f"How many of this {item_Name} would you like: "))
        return Users_Item_Quantity

#recomends the user another item, depending on what item the user purchased
def give_recommendation():
    recommended_list = get_Recommended_List()
    if len(recommended_list) == 0 :
        Checkout(chosen_items)
    for item_Type in recommended_list:
        jsonData = get_json_data(item_Type)
        user_Confirms_Recommendation = input(f"Would you like a {item_Type} with your {jsonData['Item_Pair']} (Y/N): ").upper()
        while user_Confirms_Recommendation !="Y" and user_Confirms_Recommendation !="N":
            print("Your input is invalid")
            user_Confirms_Recommendation = input(f"Would you like a {item_Type} with your {jsonData['Item_Pair']} (Y/N): ").upper()
        if user_Confirms_Recommendation == "Y":
            show_Menu(item_Type)
            manageUserInput()
            
        if user_Confirms_Recommendation == "N":
            user_confirms_Checkout = input("Would you like to head to checkout? (Y/N): ").upper()
            if user_confirms_Checkout == "Y":
                Checkout(chosen_items)
            if user_confirms_Checkout == "N":
                printMenu()
                manageUserInput()

#updates the 'Item_Stock' of the items that were purchased in the json files
def update_item_stock():
    for item_Code in chosen_items.keys(): 
        item_Data = getItemData(item_Code)
        item_Stock = item_Data["Item_Stock"]
        item_Name = item_Data["Item_Name"]
        item_Stock_Left = item_Stock-chosen_items[item_Code]
        print(f"The stock left of {item_Name} is {item_Stock_Left}")
        #item_Data["Item_Stock"]=item_Stock_Left
        item_Data.update({"Item_Stock":item_Stock_Left})
    override_json_data()

#writes the updated data / override onto the specific json file
def write_json_data(item_Type,data):
    with open("Item_Data" + f"/{item_Type}.json", "w") as json_file:
        dictionary=json.dumps(data,indent=4)
        json_file.write(dictionary)

#compares the quantity of the item baught and the stock available
def is_stock_enough(item_Code, quantity_Of_Chosen_Item):
    item_Data = getItemData(item_Code)
    item_Stock = item_Data["Item_Stock"]
    return item_Stock>=quantity_Of_Chosen_Item


#Overrides the json file depending on what items are in chosen_item
def override_json_data():
    for item_Code in chosen_items.keys(): 
        item_Data = getItemData(item_Code)
        item_Stock = item_Data["Item_Stock"]
        item_Name = item_Data["Item_Name"]
        item_Type = item_Data["Item_Type"]
        json_Item_Data_File = get_json_data(item_Type)
        json_data_item_list = json_Item_Data_File["Items"]
        for json_Item_Data in json_data_item_list:
            json_data_item_Name = json_Item_Data["Item_Name"]
            if item_Name == json_data_item_Name:
                    json_Item_Data.update({"Item_Stock":item_Stock})
                    write_json_data(item_Type,json_Item_Data_File)
                    break

#Shows a menu about recommended item depending on chosen_item
def show_Menu(item_Type):
    jsonData = get_json_data(item_Type)
    for index, item_Data in enumerate(jsonData["Items"]):
        item_Code_Letter = item_Type[0]
        item_Code_Number = index + 1
        item_Code = f"{item_Code_Letter}{item_Code_Number}"
        item_Name = item_Data["Item_Name"]
        item_Price = item_Data["Item_Price"]
        item_Stock = item_Data["Item_Stock"]
        print(f'[{item_Code}]{item_Name}\tPrice:{item_Price}\tStock:{item_Stock}')

#Removes item_type duplicates in chosen_items and gives out the list
def filter_Duplicate_Item_Type():
    unique_item_types = [] 
    for item_Code in chosen_items.keys(): 
        item_Data = getItemData(item_Code)
        item_Type = item_Data["Item_Type"]
        if item_Type not in unique_item_types: 
            unique_item_types.append(item_Type) 
    # print(non_duplicate_item_types)
    return unique_item_types

#Uses the item_type from filter_Duplicate_Item_Type and gives a list of items
#that pairs with by using 'Item_Pair' from the json data
def get_Recommended_List():
    item_Type_List = filter_Duplicate_Item_Type()
    recommended_List = []
    for item_type in item_Type_List:
        jsonData = get_json_data(item_type)
        if not jsonData["Item_Pair"] in item_Type_List:
            recommended_List.append(jsonData["Item_Pair"])
    return recommended_List


#Returns the item data from data
def getItemData(item_code):
   # Example Data
    # {
# "B1": 
#     {
#         "Item_Type": "Bisuit",
#         "Item_Name":"Fita", 
#         "Item_Price":3,
#         "Item_Stock": 3
#     }
#     ,
# "B2": 
#     {
#         "Item_Type": "Bisuit",
#         "Item_Name":"Fita", 
#         "Item_Price":3,
#         "Item_Stock": 3
#     }
# }
   return data[item_code]

#calculates the total cost of chosen items by using the prices from the json data
def Total_Cost(chosen_items:dict):
    total_cost=0
    #Calculates total cost
    for item_code in chosen_items.keys():
        item_Data=getItemData(item_code)
        item_price = item_Data["Item_Price"]
        item_Quantity = chosen_items[item_code]
        total_cost = total_cost + (item_price * item_Quantity)
    return total_cost

#Displays quantity of items are bought, what items were baught
#Total cost and the users change
def Checkout(chosen_items:dict):
    update_item_stock()
    print("You bought:")
    #Prints out all items bought
    for item_code in chosen_items.keys():
        item_Data = getItemData(item_code)
        item_Quantity = chosen_items[item_code]
        item_Name = item_Data["Item_Name"]
        print(f"{item_Name} x {item_Quantity}")
    total_cost=Total_Cost(chosen_items)
    print(f"with total cost of : {total_cost}dhs")
    print(f"Users change is : {Money-total_cost}dhs")


#Main
if __name__== "__main__":
    Money = int(input("Insert money: "))
    preload_data()
    printMenu()
    manageUserInput()



