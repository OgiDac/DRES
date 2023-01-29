from Engine import app
from multiprocessing import Process
from Engine.routes import queue, transactionProcess

process = Process(target=transactionProcess, args=(queue, ))

if __name__ == '__main__':

    process.start()
    print("ZAPOCET PROCES")
    app.run(debug=True , port=5001)
