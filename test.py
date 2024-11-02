#from langchain_huggingface import HuggingFaceEmbeddings
#from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
##from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.chains import RetrievalQA,  ConversationalRetrievalChain
#from langchain.memory import ConversationBufferMemory
#from langchain_huggingface import HuggingFaceEndpoint
#from langchain_community.document_loaders import TextLoader
#from langchain_community.document_loaders import PyPDFLoader
#from langchain_community.document_loaders.csv_loader import CSVLoader
from loader import load_db

BUTTON_WIDTH = 125

import panel as pn
import param

class cbfs(param.Parameterized):
    chat_history = param.List([])
    answer = param.String("")
    db_query = param.String("")
    db_response = param.List([])

    file_list = param.List([])
    loaded_files = param.List([])
    filenames = param.List([])

    # Text input for custom file name
    file_name = param.String(default="query_output.txt", doc="File name to save the output")

    # used to place objects on the right side of page.
    spacer = pn.layout.Spacer(width=500)

    def __init__(self, **params):
        super(cbfs, self).__init__(**params)
        self.panels = []

        self.inp = pn.widgets.TextInput(placeholder='Enter text here…')

        #self.file_input = pn.widgets.FileInput(accept='.pdf')
        self.file_input = pn.widgets.FileInput()
        self.add_button = pn.widgets.Button(name='Add', button_type='primary')
        self.add_button.on_click(self.add_item)
        self.remove_button = pn.widgets.Button(name="Remove", button_type='primary')
        self.remove_button.on_click(self.remove_item)

        self.button_load = pn.widgets.Button(name="Load DB", button_type='primary')
        self.bound_button_load = pn.bind(self.call_load_db, self.button_load.param.clicks)

        self.button_clearhistory = pn.widgets.Button(name="Clear History", button_type='warning')
        self.button_clearhistory.on_click(self.clr_history)

        self.conversation = pn.bind(self.convchain, self.inp)

        self.item_display = pn.pane.Markdown("No items added yet")
        self.loaded_file= "dummy.csv"
        #self.loaded_file = "<ENTER PATH TO LOCAL PDF HERE>"
        self.qa = load_db([self.loaded_file], "stuff", 1)
        #self.jpg_pane = pn.pane.Image('img/convchain.jpg')

        # Save button logic
        self.save_button = pn.widgets.Button(name="Save to File", button_type="success", disabled=True)
        self.save_button.on_click(self.save_to_file)
        self.save_display = pn.pane.Markdown("No saves made yet", width=500)
        self.save_filename = pn.widgets.TextInput.from_param(self.param.file_name, placeholder="Enter file name")

        self.tab1 = pn.Column(
            pn.Row(self.inp),
            pn.layout.Divider(),
            pn.panel(self.conversation, loading_indicator=True, height=300),
            pn.layout.Divider(),
            pn.Row(self.spacer, self.save_filename, self.save_display),
            pn.Row(self.spacer, self.save_button)
        )
        self.tab2 = pn.Column(
            pn.panel(self.get_lquest),
            pn.layout.Divider(),
            pn.panel(self.get_sources),
        )
        self.tab3 = pn.Column(
            pn.panel(self.get_chats),
            pn.layout.Divider(),
        )
        self.tab4 = pn.Column(
            pn.Row(self.file_input, self.add_button, self.remove_button, self.button_load,
                   self.bound_button_load),
            pn.panel(self.item_display),
            pn.Row(self.button_clearhistory, pn.pane.Markdown("Clears chat history. Can use to start a new topic")),
            pn.layout.Divider(),
            #pn.Row(self.jpg_pane.clone(width=400))
        )

        self.dashboard = pn.Column(
            pn.Row(pn.pane.Markdown('# ChatWithYourData_Bot')),
            pn.Tabs(('Conversation', self.tab1),
                    ('Database', self.tab2),
                    ('Chat History', self.tab3),
                    ('Configure', self.tab4))
        )

    def add_item(self, event):
        self.file_list.append(self.file_input.value)
        self.filenames.append(self.file_input.filename)
        #print(self.file_input.filename)
        #print(len(self.file_list), len(self.filenames))
        #print(self.filenames)
        #file_input.value = '
        #file_input.filename = ''
        self.update_display()

    def remove_item(self, event):
        current_flist = self.file_input.value
        self.file_list = [item for item in self.file_list if item != current_flist]

        current_fnlist = self.file_input.filename
        self.filenames = [item for item in self.filenames if item != current_fnlist]
        self.update_display()


    def update_display(self):
        if not self.filenames:
            self.item_display.object = "Using Default"
        else:
            self.item_display.object = "\n".join(f"- {fn}" for fn in self.filenames)

    def call_load_db(self, count):
        if count == 0 or len(self.file_list)==0:  # init or no file specified :
            return pn.pane.Markdown(f"Loaded File: {self.loaded_file}")
        else:
            #print(file_list)
            self.loaded_files = []
            for i, file in enumerate(self.file_list):
                ext = self.filenames[i].split('.')[1] # get the corresponding filename from the file_list and split.
                temp_name = "temp" + str(i) + "." + ext
                with open(temp_name, "wb") as f:
                    f.write(file)
                #file.save(temp_name)  # local copy
                #self.filenames.append(file.filename)
                self.loaded_files.append(temp_name)
            #print(self.loaded_files)
            self.button_load.button_style = 'outline'
            self.qa = load_db(self.loaded_files, "stuff", 1)
            self.button_load.button_style = "solid"
        return pn.pane.Markdown(f"Loaded Files: {self.filenames}")

    def convchain(self, query):
        if not query:
            return pn.WidgetBox(pn.Row('User:', pn.pane.Markdown("",
                                                                 width=600)), scroll=True)
        result = self.qa({"question": query, "chat_history": self.chat_history})
        self.chat_history.extend([(query, result["answer"])])
        self.db_query = result["generated_question"]
        self.db_response = result["source_documents"]
        self.answer = result['answer']
        print(self.answer)
        self.panels.extend([
            pn.Row('User:', pn.pane.Markdown(query, width=600)),
            pn.Row('ChatBot:', pn.pane.Markdown(self.answer, width=600))
        ])
        #self.add_query_result()
        self.inp.value = ''  # clears loading indicator when cleared
        return pn.WidgetBox(*self.panels, scroll=True)

    def add_query_result(self):
        """Add the current query result to the output display."""
        self.all_results = []
        if self.chat_history:  # Avoid empty inputs
            for exchange in self.chat_history:
                #print(exchange[0])
                self.all_results.append(exchange)

            # Enable save button once we have at least one query
            self.save_button.disabled = False

    def save_to_file(self, event):
        """Save the current list of queries to a user-specified file."""
        # Ensure the file has a valid name
        file_name = self.file_name.strip()
        if not file_name:
            file_name = "query_output.txt"
        elif not file_name.endswith(".txt"):
            file_name += ".txt"

        # Save the content to the file
        with open(file_name, "w") as f:
            #f.write("\n".join(self.all_results))
            f.write("\n\n".join([x[0] + ':' + x[1] for x in self.all_results]))

        # Notify the user that the output has been saved
        self.save_display.object = f"\n\n**Output saved to {self.file_name}**"

    @param.depends('db_query', )
    def get_lquest(self):
        if not self.db_query:
            return pn.Column(
                pn.Row(pn.pane.Markdown(f"Last question to DB:")),
                pn.Row(pn.pane.Str("no DB accesses so far"))
            )
        return pn.Column(
            pn.Row(pn.pane.Markdown(f"DB query:")),
            pn.pane.Str(self.db_query)
        )

    @param.depends('convchain', 'clr_history')
    def get_chats(self):
        if not self.chat_history:
            return pn.WidgetBox(pn.Row(pn.pane.Str("No History Yet")), width=600, scroll=True)
        rlist = [pn.Row(pn.pane.Markdown(f"Current Chat History variable"))]
        for exchange in self.chat_history:
            rlist.append(pn.Row(pn.pane.Str(exchange)))
        return pn.WidgetBox(*rlist, width=600, scroll=True)

    @param.depends('db_response', )
    def get_sources(self):
        if not self.db_response:
            return
        rlist = [pn.Row(pn.pane.Markdown(f"Result of DB lookup:"))]
        for doc in self.db_response:
            rlist.append(pn.Row(pn.pane.Str(doc)))
        return pn.WidgetBox(*rlist, width=600, scroll=True)

    def clr_history(self, count=0):
        self.chat_history = []
        self.all_results = []
        return

cb = cbfs()

cb.dashboard.servable()
