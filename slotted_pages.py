import random
import webbrowser
import os

start_html = '''
<html>
<head>
<style>
.solution {
  display: none;
}
.green {
  color:green
}
.red {
  color:red
}
.left-border {
  padding-left: 20px;
}
.queuebox {
border: black solid
'''
start_html += "width: " + str(20) + "%;"

start_html += '''
border: solid black;
margin-top: 10px;
margin-bottom: 10px;
}
.border {
    border: solid black;
    padding: 10px;
    width: 50%;
}
button {
    margin: 10px;
}
</style>
</head>
<body>
<h1>Slotted Pages</h1>
'''

end_html = '''
<script>
function myFunction() {
  var x = document.getElementById("solution");
  if (x.style.display === "block") {
    x.style.display = "none";
  } else {
    x.style.display = "block";
  }
}
</script>
</body>
</html>
'''

solution_html = ""

tid_size = 4
header_size = 8

aligned_struct = []
struct_size = 0

amount_of_pages = 3

def generate_data_struct():
    global aligned_struct, struct_size
    aligned_struct.append(random.randint(4,5))
    aligned_struct.append(random.randint(2,3))
    aligned_struct.append(1)
    for i in aligned_struct:
        struct_size += i

def print_instructions():
    global solution_html
    copy_struct = aligned_struct.copy()
    random.shuffle(copy_struct)
    solution_html += "<h4> Datastruct: { \n"
    for i in copy_struct:
        if(i == 1):
            solution_html += "Available: 1B "
        elif(i < 4):
            solution_html += "Amount of Work:" + str(i) + "B "
        else:
            solution_html += "Id:" + str(i) +"B "
    solution_html += "} </h4>"

def return_hex(value, size):
    if(size == 2):
        return format(value, 'X').zfill(size)
    if(size == 4):
        hex = format(value, 'X').zfill(size)
        return [hex[0] + hex[1], hex[2] + hex[3]]
    return ""


def generate_data():
    data = []
    byte_aligned_data = []
    for i in aligned_struct:
        random_int = random.randint(0, ((16**2)**i)-1)
        data.append(format(random_int, 'X').zfill(i*2))
    for i in data:
        j = 0
        while(j < len(i)):
            byte_aligned_data = byte_aligned_data + [i[j] + i[j+1]]
            j += 2
    padding = []
    while(len(byte_aligned_data+padding)%8 != 0):
        padding = padding + ["00"]
    return [byte_aligned_data , padding]

def generate_slot_id():
    id = ["00"]
    random_int = random.randint(0, ((16**2))-1)
    id = id + [format(random_int, 'X').zfill(2)]
    return id

def print_hex(value, curr_byte):
    global solution_html
    if(curr_byte == 0):
        solution_html += "<tr><td> 0x00 </td><td class='left-border'>" + value + "</td>"
    elif(curr_byte%16 == 0):
        solution_html += "</tr><tr><td>0x" + return_hex(curr_byte, 2) + "</td><td class='left-border'>" + value + "</td>"
    elif(curr_byte %8 == 0):
        solution_html += "<td class='left-border'>" + value + "</td>"
    else:
        solution_html += "<td>" + value + "</td>"
    return curr_byte + 1

class slot:
    redirected: bool
    was_redirected: bool
    offset: int
    size_of_data: int
    data: list

    def __init__(self, redirected, was_redirected, offset, data):
        self.redirected = redirected
        self.was_redirected = was_redirected
        self.offset = offset
        self.data = data
        self.size_of_data = len(data[0]) #2 hexchars => 1 byte

    def get_slot_representation(self):
        if(self.redirected):
            return self.data
        else:
            return ["FF", ("FF" if self.was_redirected else "00"), return_hex(self.offset, 2), return_hex(self.size_of_data, 2)]

class slottedpage():
    page_size: int
    space_left: int
    slots: list
    data_start: int
    id: list

    def __init__(self, id):
        self.page_size = 16*8 #8 rows with 16bytes
        self.space_left = self.page_size - header_size #header is 8bytes 0-7
        self.slots = []
        self.data_start = self.page_size
        self.id = id

    def potential_space_left(self, size, redirected, size_of_data):
        # free space - slot - (slot for redirection if it was redirected) - data
        return self.space_left - (size + (0 if redirected else size_of_data)) 

    def insert_data(self, redirected, was_redirected, data):
        size_of_data = len(data[0]) + len(data[1])
        pot_space_left = self.potential_space_left(tid_size, redirected, size_of_data)
        if(pot_space_left >= 0):
            self.data_start -= 0 if redirected else size_of_data
            new_slot = slot(redirected, was_redirected, 0 if redirected else self.data_start, data)
            self.slots.append(new_slot)
            self.space_left = pot_space_left
            return new_slot.get_slot_representation()
        else:
            return []

    def print_slotted_page(self):
        global solution_html
        curr_byte = 0
        slot_rep = []
        data = []
        for slot in self.slots:
            slot_rep += slot.get_slot_representation()
            if not slot.redirected:
                data = slot.data + data

        solution_html += "<h4> Page: 0x" + "".join(self.id) + ':</h4> <table>'
        for i in range(0, header_size):
            curr_byte = print_hex("XX", curr_byte)

        for i in range(len(slot_rep)):
            curr_byte = print_hex(slot_rep[i], curr_byte)

        while(curr_byte != self.data_start):
            curr_byte = print_hex("00", curr_byte)

        for i in data:
            for entry in i:
                curr_byte = print_hex(entry, curr_byte)
        solution_html += "</tr></table>"

def generate_normal_slot(slot_page):
    data = generate_data()
    tid = slot_page.insert_data(False, False, data)
    return slot_page.id + return_hex(len(slot_page.slots)-1, 4) + tid + data[0]

def generate_redirection(slot_page1, slot_page2):
    redirect_list = slot_page2.id + return_hex(len(slot_page2.slots), 4)
    redirected_list = slot_page1.id + return_hex(len(slot_page1.slots), 4)
    tid = slot_page1.insert_data(True, False, redirect_list)
    data = generate_data()
    data[0] = redirected_list + data[0]
    tid2 = slot_page2.insert_data(False, True, data)
    return redirected_list + tid + tid2 + data[0]


generate_data_struct()
print_instructions()

slotted_pages = []

for i in range(amount_of_pages):
    slot_id = generate_slot_id()
    slotted_pages.append(slottedpage(slot_id))

#biggest insertion is was redirected
#1tid + redirected tid + struct
max_space_req = (tid_size*2) + struct_size

last_page = 1000
not_full = True

normal_tasks = []
redirect_tasks = []
while not_full:
    type_of_op = random.randint(0,1)
    if(type_of_op == 0):
        page_no = random.choice([i for i in range(0,len(slotted_pages)) if i != last_page])
        last_page = page_no
        normal_tasks.append(generate_normal_slot(slotted_pages[page_no]))
    else:
        page_no = random.choice([i for i in range(0,len(slotted_pages)) if i != last_page])
        page_no2 = random.choice([i for i in range(0,len(slotted_pages)) if i != page_no])
        last_page = page_no
        redirect_tasks.append(generate_redirection(slotted_pages[page_no], slotted_pages[page_no2]))
    for i in slotted_pages:
        if i.space_left < max_space_req:
            not_full = False
            break

for i in range(amount_of_pages):
    slotted_pages[i].print_slotted_page()

task_1 = normal_tasks[random.randint(0,len(normal_tasks)-1)]
data_element = random.randint(0,2)

if(data_element == 0):
    solution_html += "<h4>1. Find the id at: " + "".join(task_1[0:4]) + "</h4>"
elif(data_element == 1):
    solution_html += "<h4>1. Find the amount of work at: " + "".join(task_1[0:4]) + "</h4>"
elif(data_element == 2):
    solution_html += "<h4>1. Find the availability at: " + "".join(task_1[0:4]) + "</h4>"

task_2 = redirect_tasks[random.randint(0,len(redirect_tasks)-1)]
data_element2 = random.randint(0,2)

if(data_element2 == 0):
    solution_html += "<h4>2. Find the id at: " + "".join(task_2[4:8]) + "</h4>"
elif(data_element2 == 1):
    solution_html += "<h4>2. Find the amount of work at: " + "".join(task_2[4:8]) + "</h4>"
elif(data_element2 == 2):
    solution_html += "<h4>2. Find the availability at: " + "".join(task_2[4:8]) + "</h4>"

task_3 = redirect_tasks[random.randint(0,len(redirect_tasks)-1)]
data_element3 = random.randint(0,2)

if(data_element3 == 0):
    solution_html += "<h4>3. Find the id at: " + "".join(task_3[0:4]) + "</h4>"
elif(data_element3 == 1):
    solution_html += "<h4>3. Find the amount of work at: " + "".join(task_3[0:4]) + "</h4>"
elif(data_element3 == 2):
    solution_html += "<h4>3. Find the availability at: " + "".join(task_3[0:4]) + "</h4>"

solution_html += "<h2>Solution: </h2> <button onclick='myFunction()'>Show solution</button> <div id='solution' class='solution'>"

if(data_element == 0):
    solution_html += "<h4>1. The id is: " + "".join(task_1[8:8+aligned_struct[0]])  + "</h4>"
elif(data_element == 1):
    offset = 8+aligned_struct[0]
    end = offset+aligned_struct[1]
    solution_html += "<h4>1. The amount of work is: " + "".join(task_1[offset:end])  + "</h4>"
elif(data_element == 2):
    offset = 8+aligned_struct[0]+aligned_struct[1]
    end = offset+aligned_struct[2]
    solution_html += "<h4>1. The availability is: " + "".join(task_1[offset:end])  + "</h4>"

if(data_element2 == 0):
    solution_html += "<h4>2. The id is: " + "".join(task_2[12:12+aligned_struct[0]])  + "</h4>"
elif(data_element2 == 1):
    offset = 12+aligned_struct[0]
    end = offset+aligned_struct[1]
    solution_html += "<h4>2. The amount of work is: " + "".join(task_2[offset:end])  + "</h4>"
elif(data_element2 == 2):
    offset = 12+aligned_struct[0]+aligned_struct[1]
    end = offset+aligned_struct[2]
    solution_html += "<h4>2. The availability is: " + "".join(task_2[offset:end])  + "</h4>"

if(data_element3 == 0):
    solution_html += "<h4>3. The id is: " + "".join(task_3[12:12+aligned_struct[0]])  + "</h4>"
elif(data_element3 == 1):
    offset = 12+aligned_struct[0]
    end = offset+aligned_struct[1]
    solution_html += "<h4>3. The amount of work is: " + "".join(task_3[offset:end])  + "</h4>"
elif(data_element3 == 2):
    offset = 12+aligned_struct[0]+aligned_struct[1]
    end = offset+aligned_struct[2]
    solution_html += "<h4>3. The availability is: " + "".join(task_3[offset:end])  + "</h4>"

solution_html += "</div>"

file = open("exercise.html","w")

file.write(start_html)
file.write(solution_html)
file.write(end_html)

file.close()

path = os.path.dirname(os.path.abspath(__file__)) + "/exercise.html"
url = "file://" + path
webbrowser.open(url, new=2) 