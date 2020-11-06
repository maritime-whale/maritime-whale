def log(filename, msg):
    f = open(filename, "a")
    f.write(msg + "\n")
    f.close()
