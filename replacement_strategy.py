import random
import webbrowser
import os

#this file generates exercises for different buffer replacement strategies
number_of_pages = 7
number_of_operations = 30
#multiples of 2 for 2q needed
size_of_queue = 4
fixxed_pages = []

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
.queuebox {
box-sizing: border-box;
display: inline-block;
padding: 10px;
text-align: center;
'''
start_html += "width: " + str((100-5)/size_of_queue) + "%;"

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
<h1>Buffer Replacement</h1>
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
#class to represent a page
class page:
    id: int
    marked: bool
    in_memory: bool
    number_of_access: int
    def __init__(self, id):
        self.marked = False
        self.id = id
        self.in_memory = False
        self.number_of_access = 0

class operation:
    page_number: int
    type: int
    def __init__(self, page_number, type):
        self.page_number = page_number
        self.type = type

    def print(self):
        global solution_html
        if self.type == 0:
            solution_html += "<h4>Fixing Page:" + str(self.page_number) + "</h4>"
        else:
            solution_html += "<h4>Unfixing Page:" + str(self.page_number) + "</h4>"

class fifo_queue:
    queue: list
    size: int
    def __init__(self):
        self.queue = []
        self.size = 0

    def fix_page(self, value, verbose):
        global solution_html, fixxed_pages
        if value in self.queue:
            value.in_memory = True
            if value not in fixxed_pages:
                fixxed_pages.append(value)
            return True

        if self.size == size_of_queue:
            for i in range(0, self.size):
                if not self.queue[i].in_memory:
                    self.queue.pop(i)
                    self.size -= 1
                    break

        if self.size != size_of_queue:
            value.in_memory = True
            self.queue.append(value)
            self.size += 1
            if value not in fixxed_pages:
                fixxed_pages.append(value)
            return True
        else:
            if verbose:
                solution_html += "<h4>Cant throw out any page</h4>"
            return False

    def unfix_page(self, value):
        global fixxed_pages
        if value in self.queue:
            value.in_memory = False
            fixxed_pages.remove(value)


    def print(self):
        global solution_html
        solution_html += "<div class='border'> <h4> Fixxed Pages : {"
        for i in range(0, self.size):
            if self.queue[i].in_memory:
                solution_html += str(self.queue[i].id) + " "
        solution_html += "} </h4>"
        solution_html += "<div> \n"
        for i in range(0,self.size):
            solution_html += '<div class="queuebox"><p>' + str(self.queue[i].id) + '</p></div> \n'
        solution_html += "</div> \n </div>\n"

class lru_queue(fifo_queue):
    def __init__(self):
        self.queue = []
        self.size = 0

    def unfix_page(self, value):
        if value in self.queue:
            super(lru_queue, self).unfix_page(value)
            self.queue.remove(value)
            self.queue.append(value)

class lfu_queue(fifo_queue):
    def __init__(self):
        self.queue = []
        self.size = 0

    def fix_page(self, value, verbose):
        if value not in self.queue:
            value.number_of_access = 1
        else:
            value.number_of_access += 1
        self.queue.sort(key=lambda x: x.number_of_access, reverse=False)
        super(lfu_queue, self).fix_page(value, verbose)

    def print(self):
        global solution_html
        solution_html += "<div class='border'> <h4> Fixxed Pages : {"
        for i in range(0, self.size):
            if self.queue[i].in_memory:
                solution_html += str(self.queue[i].id) + " "
        solution_html += "} </h4>"
        solution_html += "<div> \n"
        for i in range(0,self.size):
            solution_html += '<div class="queuebox"><p>' + str(self.queue[i].id) + '</p> <p class="green">' + str(self.queue[i].number_of_access) + '</p></div> \n'
        solution_html += "</div> \n </div>\n"

class second_chance_queue(fifo_queue):
    pointer: int
    def __init__(self):
        self.queue = []
        self.size = 0
        self.pointer = 0

    def increase_pointer(self):
        if(self.pointer == size_of_queue-1):
            self.pointer = 0
        else:
            self.pointer += 1

    def fix_page(self, value, verbose):
        global solution_html, fixxed_pages
        if value in self.queue:
            value.in_memory = True
            if value not in fixxed_pages:
                fixxed_pages.append(value)
            return True

        if self.size == size_of_queue:
            amount_of_full_pages = 0
            for i in range(0, self.size):
                if self.queue[i].in_memory:
                    amount_of_full_pages += 1
            if amount_of_full_pages == self.size:
                if verbose:
                    solution_html += "<h4>Cant throw out any page</h4>"
                return False
            else:
                while True:
                    if not self.queue[self.pointer].in_memory:
                        if self.queue[self.pointer].marked:
                            self.queue[self.pointer].marked = False
                        else:
                            self.queue[self.pointer] = value
                            self.increase_pointer()
                            if value not in fixxed_pages:
                                fixxed_pages.append(value)
                            return True
                    self.increase_pointer()

        if self.size != size_of_queue:
            value.in_memory = True
            self.queue.append(value)
            self.size += 1
            if value not in fixxed_pages:
                fixxed_pages.append(value)
            self.increase_pointer()
            return True

    def print(self):
        global solution_html
        solution_html += "<div class='border'> <h4> Fixxed Pages : {"
        for i in range(0, self.size):
            if self.queue[i].in_memory:
                solution_html += str(self.queue[i].id) + " "
        solution_html += "} </h4>"
        solution_html += "<h4> Pointer at:" + str(self.pointer) + "</h4>"
        solution_html += "<div> \n"
        for i in range(0,self.size):
            solution_html += '<div class="queuebox"><p>' + str(self.queue[i].id) + ("</p> <p class='green'> X" if self.queue[i].marked else "</p> <p class='red'> O") + '</p></div> \n'
        solution_html += "</div> \n </div>\n"
            

    def unfix_page(self, value):
        if value in self.queue:
            super(second_chance_queue, self).unfix_page(value)
            value.marked = True

class two_queue():
    fifo: fifo_queue
    lru: lru_queue
    size: int
    queue: list
    def __init__(self):
        self.fifo = fifo_queue()
        self.queue = self.fifo.queue
        self.lru = lru_queue()
        self.size = 0

    def fix_page(self, value, verbose):
        if value in self.fifo.queue:
            if self.lru.fix_page(value, verbose):
                self.fifo.queue.remove(value)
                self.fifo.size -= 1
        elif value in self.lru.queue:
            self.lru.fix_page(value, verbose)
        else:
            self.fifo.fix_page(value, verbose)
        self.size = self.fifo.size

    def unfix_page(self, value):
        if value in self.fifo.queue:
            self.fifo.unfix_page(value)
        elif value in self.lru.queue:
            self.lru.unfix_page(value)
        self.size = self.fifo.size

    def print(self):
        global solution_html, fixxed_pages
        solution_html += "<div class='border'> <h4> Fixxed Pages : {"
        for i in fixxed_pages:
            solution_html += str(i.id) + " "
        solution_html += "} </h4>"
        solution_html += "<div> <h3> Fifo queue <h3>\n"
        for i in range(0,len(self.fifo.queue)):
            solution_html += '<div class="queuebox"><p>' + str(self.fifo.queue[i].id) + '</p></div> \n'
        solution_html += "</div> <div> <h3> LRU queue <h3>\n"
        for i in range(0,len(self.lru.queue)):
            solution_html += '<div class="queuebox"><p>' + str(self.lru.queue[i].id) + '</p></div> \n'
        solution_html += "</div> \n </div>\n"

#generate pages
pages = []
for i in range(0,number_of_pages):
    pages.append(page(i))

type = input('Which queue would you like to test? fifo,lru,lfu,second,2q\n')

starting_order = []
operation_order = []
fixxed_pages = []

if(type == "fifo"):
    queue_test = fifo_queue()
    queue_actual = fifo_queue()
    solution_html += "<h2> Insert the following values into the fifo queue: </h2>\n"
elif(type == "lru"):
    queue_test = lru_queue()
    queue_actual = lru_queue()
    solution_html += "<h2> Insert the following values into the lru queue: </h2>\n"
elif(type == "lfu"):
    queue_test = lfu_queue()
    queue_actual = lfu_queue()
    solution_html += "<h2> Insert the following values into the lfu queue: </h2>\n"
    solution_html += "<p> Updating frequency and sorting is done at fix page </p>\n"
elif(type == "second"):
    queue_test = second_chance_queue()
    queue_actual = second_chance_queue()
    solution_html += "<h2> Insert the following values into the second chance queue: </h2>\n"
elif(type == "2q"):
    size_of_queue = size_of_queue/2
    queue_test = two_queue()
    queue_actual = two_queue()
    solution_html += "<h2> Insert the following values into the two queue(fifo, lru): </h2>\n"
    solution_html += "<p> Updating lru is only done when page on lru is unfixed </p>\n"

solution_html += "<p> Fixxing multiple times still only requires one unfix: </p>\n"
while queue_test.size != size_of_queue:
    page_to_insert = pages[random.randint(0,number_of_pages-1)]
    if(page_to_insert not in fixxed_pages):
        queue_test.fix_page(page_to_insert, False)
        starting_order.append(page_to_insert.id)
for i in queue_test.queue.copy():
    queue_test.unfix_page(i)
    i.marked = False

solution_html += "<h2> Start Queue </h2>\n"
queue_test.print()
solution_html += "<h2>Order of operations: </h2>"
for i in range(0,number_of_operations):
    if len(fixxed_pages) != 0 and random.randint(0,1) == 1:
        curr_op = operation(fixxed_pages[random.randint(0,len(fixxed_pages)-1)].id,1)
        curr_op.print()
        operation_order.append(curr_op)
        curr_page = pages[curr_op.page_number]
        queue_test.unfix_page(curr_page)
    else:
        curr_op = operation(random.randint(0,number_of_pages-1),0)
        operation_order.append(curr_op)
        curr_op.print()
        curr_page = pages[curr_op.page_number]
        curr_page.in_memory = queue_test.fix_page(curr_page, False)

fixxed_pages = []
solution_html += "<h2>Solution: </h2> <button onclick='myFunction()'>Show solution</button> <div id='solution' class='solution'>"
for i in starting_order:
    queue_actual.fix_page(pages[i], False)
for i in queue_actual.queue.copy():
    queue_actual.unfix_page(i)
    i.marked = False
queue_actual.print()
for i in range(0,number_of_operations):
    curr_op = operation_order[i]
    curr_op.print()
    if curr_op.type == 0:
        queue_actual.fix_page(pages[operation_order[i].page_number], True)
    else: 
        queue_actual.unfix_page(pages[operation_order[i].page_number])
    queue_actual.print()
solution_html += "</div>"

file = open("exercise.html","w")

file.write(start_html)
file.write(solution_html)
file.write(end_html)

file.close()

path = os.path.dirname(os.path.abspath(__file__)) + "/exercise.html"
url = "file://" + path
webbrowser.open(url, new=2) 