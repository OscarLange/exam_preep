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
.queuebox {
box-sizing: border-box;
display: inline-block;
padding: 10px;
text-align: center;
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
<h1>Linear Hashing</h1>
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


bucket_size = int(input('What bucket size do you want? (1,2,....)\n'))
#limit to 26 for every char in alphabet
#you can go higher but will produce special chars
amount_of_values = int(input('What amount of inserts do you want? (1-26)\n'))
max_chain_length = int(input('What size of chains do you want before split? (1==1Bucket before split)\n'))
exponent = 6

solution_html += "<h2> Insert the following values into the hashtable: </h2>\n"
solution_html += "<p> Bucket size: " + str(bucket_size) +" and splitting as soon as a bucket is full and the chain is size" + str(max_chain_length) +"</p>\n"

keys = []
bin_keys = []
values = list(map(chr, range(65, 65+amount_of_values)))

for i in range(0, amount_of_values):
    key = random.randint(0,2**exponent)
    keys.append(key)
    bin_keys.append(bin(key)[2:].zfill(exponent))

for i in range(0, amount_of_values):
    solution_html += "<h4> Insert:" + str(keys[i]) + "=>" + values[i] + "</h4>\n"

class bucket_entry():
    size: int
    values: list
    def __init__(self):
        self.size = bucket_size
        self.values = []

    def insert(self, value):
        if len(self.values) != self.size:
            self.values.append(value)
            return True
        return False

    def print(self):
        global solution_html
        solution_html += '<div class="queuebox"><p>'
        for value in self.values:
            solution_html += str(value) + " "
        solution_html += '</p> </div>'

class hashentry():
    key: str
    key_size: int
    chains: list

    def __init__(self, key, key_size):
        self.key = key
        self.key_size = key_size
        self.chains = []

    def insert(self, value):
        for bucket in self.chains:
                if bucket.insert(value):
                    return len(self.chains) > max_chain_length or (len(self.chains) == max_chain_length and len(self.chains[-1].values) == self.chains[-1].size)
        new_bucket = bucket_entry()
        new_bucket.insert(value)
        self.chains.append(new_bucket)
        return len(self.chains) > max_chain_length or (len(self.chains) == max_chain_length and len(new_bucket.values) == new_bucket.size)

    def hash(self, key):
        return key[-self.key_size:] == self.key[-self.key_size:]

    def return_values(self):
        entries = []
        for bucket in self.chains:
            for entry in bucket.values:
                entries.append(entry)
        return entries

    def print(self):
        global solution_html
        solution_html += '<div class="queuebox"><p class="red">' + str(self.key) + '</p></div>'
        for bucket in self.chains:
            bucket.print()

class hashmap():
    hash_entries: list
    pointer: int

    def __init__(self):
        self.hash_entries = []
        self.hash_entries.append(hashentry("0", 1))
        self.hash_entries.append(hashentry("1", 1))
        self.pointer = 0

    def insert(self, key, value, split_allowed):
        global bin_keys, values
        self.set_pointer()
        for i in range(0, len(self.hash_entries)):
            hash_entry = self.hash_entries[i]
            if hash_entry.hash(key):
                splitting = hash_entry.insert(value)
                if(splitting and i == self.pointer and split_allowed):
                    restore_values = hash_entry.return_values()
                    old_key = hash_entry.key
                    old_key_size = hash_entry.key_size
                    self.hash_entries.remove(hash_entry)
                    self.hash_entries.append(hashentry("0" + old_key, old_key_size+1))
                    self.hash_entries.append(hashentry("1" + old_key, old_key_size+1))
                    self.hash_entries.sort(key=lambda x: int(x.key, 2))
                    for value in restore_values:
                        key = bin_keys[values.index(value)]
                        self.insert(key, value, False)

    def set_pointer(self):
        smallest_key_size = exponent
        for hash_entry in self.hash_entries:
            smallest_key_size = min(hash_entry.key_size, smallest_key_size)

        for i in range(0, len(self.hash_entries)):
            if self.hash_entries[i].key_size == smallest_key_size:
                self.pointer = i
                return

    def print(self):
        global solution_html
        solution_html += "<div class='border'> <h4> Hashmap pointer : " + str(self.pointer) + " </h4>"
        solution_html += "<div> <h4> HashMap: <h4>\n"
        for hash_entry in self.hash_entries:
            solution_html += "<div>"
            hash_entry.print()
            solution_html += "</div>"
        solution_html += "</div> \n </div>\n"

hash_map = hashmap()
hash_map.print()

solution_html += "<h2>Solution: </h2> <button onclick='myFunction()'>Show solution</button> <div id='solution' class='solution'>"
for i in range(0, amount_of_values):
    solution_html += "<h4> Insert:" + str(keys[i]) + "==" + bin_keys[i] + "==>" + values[i] + "</h4>\n"
    hash_map.insert(bin_keys[i], values[i], True)
    hash_map.print()
solution_html += "</div>"

file = open("exercise.html","w")

file.write(start_html)
file.write(solution_html)
file.write(end_html)

file.close()

path = os.path.dirname(os.path.abspath(__file__)) + "/exercise.html"
url = "file://" + path
webbrowser.open(url, new=2) 