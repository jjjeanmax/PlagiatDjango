from django.shortcuts import render
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


# to render homepage
def home(request):
    return render(request, 'homepage/homepage.html')


# to render login page
def login(request):
    return render(request, 'login/login.html')


# Declaring Global variable to be used while creating Database filename if they wish to add the file in Database
super_username = ""


# the process of validating login,and giving out proper responses
def login_logic(request):
    # to use global variable in the function
    global super_username
    found = 0  # if the user is found in login database found is initialized as 1
    # opening user login database
    login_database = open('userdatabase.txt')
    # reading out the username and password from the login html page
    # and seperating with a delemiter because thats how files are saved in database
    login_buffer = request.POST['username'] + '|' + request.POST['password']
    # initializing the global variable so that it can be used later on
    super_username = request.POST['username']
    # iterating to each user in login Database
    for user in login_database:
        # strip is used to remove the extra spaces i.e /n from that line,and we check if that is same as the entered
        # value, the value entered database is also of the form username/password
        if user.strip() == login_buffer:
            # if the value entered matches userdatabase we initialize found =1
            found = 1
    # we create dictonary to pass it to the html so that we can tell hello {username} login SUCCESSFUL
    LoginDict = {
        'username': super_username,
    }
    if found == 1:
        # if the login is SUCCESSFUL we render the next page that is where to upload the file,
        # but first we till hello username login SUCCESSFUL
        return render(request, 'plagiarism/plagiarism.html', LoginDict)
    else:
        # if the login fails we render wrong login page and ask them to login again
        return render(request, 'login/wrongLogin.html')


# to render register page
def register(request):
    return render(request, 'register/register.html')


# the process of validating if the username is not repeated and later adding them in userdatabase
def register_logic(request):
    # if the user already exists in login database, if yes found is initialized as 1
    found = 0
    # opening user login database
    login_database = open('userdatabase.txt', 'r')
    # reading the register USERNAME from HTML
    register_username = request.POST['username']
    # reading the username and password from HTML and separating with  delimiter
    register_buffer = request.POST['username'] + '|' + request.POST['password'] + '\n'
    # for checking if the user already exists in the user database
    for user in login_database:
        # separating the username from password with the given delimiter
        userlist = user.split('|')
        # taking the username frm the list and checking if it is same as the username entered in html
        if userlist[0] == register_username:
            # if yes initialize with 1
            found = 1
    login_database.close()
    # if user already exits render wrong register html and ask them to login again
    if found == 1:
        return render(request, 'register/wrongRegister.html')
    # if the user doesnt exits and the user and password in the login database
    else:
        login_database = open('userdatabase.txt', 'a')
        login_database.write(register_buffer)
        # and render login page with registration success message
        return render(request, 'login/registerSucess.html')


# Declaring global variable to get the filename used by the user
# to be used later if the user wish to add the file in the database
superFile = None
# to store each line from the file entered by the user to be used later if they wish to save in database
superList = []


# once the file is uploaded the plagiarism checking happens here
def post_upload(request):
    # to use global variable in the function
    global superFile
    global superList
    file = request.FILES['sentFile']  # the get the file uploaded by the user
    superFile = file.name  # to get the file name of the file entered to be used later if the wish to save the file

    # code to save the file in a particular directory along with its content, i made a buffer directory to save the file
    path = default_storage.save(f'bufferFolder/{file.name}', ContentFile(file.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    file = open(f'bufferFolder/{file.name}')  # opening the file saved in read mode
    buffer_lines = []  # to separate file to list of sentences

    for line in file:
        # saving the list of lines in the global SuperLines to be used later if the user wish to save the file
        superList.append(line)
        # splitting each lines with . delimiter to form sentences
        sentences = line.split('.')
        # adding this to the list of sentences
        buffer_lines.extend(sentences)
    file.close()
    # deleting the file in the buffer folder, because same filenames will create problems
    os.remove(f'{file.name}')
    # to separate sentences to list of words
    buffer_line_words = []
    # for each line is the sentences list
    for line in buffer_lines:
        # separate words with space delimiter
        buffer_words = line.split(' ')
        # removing the empty lines which just as only \n without any content
        if buffer_words != ['\n']:
            # appending the entire list of words to the list so it forms
            # [[sentence1Word1,sentence1Word2],[sentence2Word1,sentence2Word2],etc]
            buffer_line_words.append(buffer_words)
    for line_words in buffer_line_words:  # for each list containing the list of words in the MAIN LIST
        if len(line_words) <= 3:  # deleting lines which contains 3 or lesser words
            buffer_line_words.remove(line_words)
    LineCheck = []  # to see how many sentences are plagiarized for overall Percentage
    LineCount = len(buffer_line_words)  # to count total number of sentences
    for i in range(LineCount):  # making list equal to number of lines and initializing eachline to not plagiarized
        LineCheck.append(0)
    directory = 'fileDatabase'  # our file database directory
    OutputList = []  # a list containing set of statements to be displayed in HTML

    for filename in os.listdir(directory):  # for each file in the file database
        file = open(f'fileDatabase/{filename}', encoding="ISO-8859-1")  # opening that file
        buffer_lines = []  # same process as above for a different file,refer from line 75
        for line in file:
            sentences = line.split('.')
            buffer_lines.extend(sentences)
        file.close()
        destination_buffer_line_words = []
        for line in buffer_lines:
            buffer_words = line.split(' ')
            if buffer_words != ['\n']:
                destination_buffer_line_words.append(buffer_words)
        for line_words in destination_buffer_line_words:
            if len(line_words) <= 3:
                destination_buffer_line_words.remove(line_words)
        # TODO: Verifier cette logique >>> Pour le moment tout passe!
        # for number of lines plagiarized in each file
        allCount = 0
        # to iterate through the line and keep count of which line being executed and to find total number of lines
        allTotal = 0
        for eachline in buffer_line_words:  # for each line in the file entered by the user
            allTotal += 1  # to iterate through the line and to find total number of lines
            for destination_each_line in destination_buffer_line_words:  # for eachline in the database file
                count = 0  # to check how many words in a user line is there in dest vfile line
                total = 0  # total number of words in a user line
                for eachword in eachline:
                    total += 1  # to count number of words in user line
                    if eachword in destination_each_line:  # to check if the word is there dest line
                        count += 1
                if (count / total) >= .80:  # if 80 percent of user entered line is present in destination file line
                    allCount += 1  # increase the plagiarized line by 1
                    # making that line already plagiarized for the Overall plagiarism Percentage
                    LineCheck[allTotal - 1] = 1
                    # if a line is plagiarized no need to check in other lines
                    # of the same file hence stop the itertaion and go to next line
                    break

        if allTotal != 0:
            percent_plagiat = allCount / allTotal * 100  # to find percent plagiary from each file
            # Append this in the OutputList so that we can print it in HTML
            OutputList.append(
                f"The Percentage Plagiarism from {filename} is %.2f" % percent_plagiat)
    # To check how many lines in Line Check are 1, basically to see how many lines are overall plagiarized
    Final_plagiat_count = 0
    for each in LineCheck:  # to check how many lines have 1
        if each == 1:
            Final_plagiat_count += 1
    FinalOutput = "NULL"
    if LineCount != 0:
        Overallpercent_plagiat = Final_plagiat_count / LineCount * 100  # the overall Plagiarism Percentage
        # for the HTML print statements
        FinalOutput = (f"The Overall Percentage Plagiarism is %.2f" % Overallpercent_plagiat)
    else:
        FinalOutput = f"Your File {superFile} is empty "
    # its dictionary to send the OutputList to tht HTML to use it in the front end
    OutputDict = {
        "OutputList": OutputList,
        "FinalOutput": FinalOutput,
    }
    return render(request, "plagiarism/plagiarismOutput.html",
                  OutputDict)  # we render the Plagiarism Output HTML and we pass the dict to be printed in OP


# to add the file to the File Database
def add_file(request):
    OutputStatement = {
        'username': super_username,
        'filename': superFile,
    }
    # to check if the user entered yes for the add file in Database
    if request.POST['include'] == 'YES':
        # using the global variable to form a new file name, username +actual filename
        filename = super_username + "'s " + str(superFile)
        # creating a new file with the our new filename and using append func
        file = open(f'fileDatabase/{filename}', 'a')
        # using global variable to get each line from the user file
        for line in superList:
            # writing line to our new files
            file.write(line)
        # rendering file added SUCCESSFULLY message
        return render(request, 'FinalPage/FileAdded.html', OutputStatement)
    else:
        # if they choose no to add files then rendering thank you message
        return render(request, 'FinalPage/ThankYou.html', OutputStatement)
