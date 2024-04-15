from ipywidgets import Layout, Box
import ipywidgets as widgets
try:
    from loter.read_from_qcodes import ReadFromQcodes
except:
    from read_from_qcodes import ReadFromQcodes
import jsonpickle
from IPython.display import display, clear_output
import os
import qcodes as qc
try:
    from loter.read_from_qcodes import ChooseADataset
except:
    from read_from_qcodes import ChooseADataset

class ManagerClass(widgets.Box):
    ''' This class is the main class for the plotting software. It creates the Graphical User Interface and holds the overview dictionaries.
     It also has the functions to save and load the UI elements to and from a json file. 
     It is the main class that is called in the main.py file. It is a subclass of ipywidgets.Box.'''
    def __init__(self, initial_qcodes_database_name = None, initial_dataset_name = None, initial_x_axis = None, initial_y_axis = None, initial_z_axis = None,
                  initial_x_axis_label = None, initial_y_axis_label = None, initial_plot_title = None, plot_width = None, plot_height = None, 
                  data_analysis_function = None , initial_templates = None, initial_plot_colors = None, initial_plot_types = None):

        super().__init__()
        self.initial_qcodes_database_name = initial_qcodes_database_name
        self.initial_dataset_name = initial_dataset_name
        self.initial_x_axis = initial_x_axis
        self.initial_y_axis = initial_y_axis
        self.initial_z_axis = initial_z_axis
        self.initial_x_axis_label = initial_x_axis_label
        self.initial_y_axis_label = initial_y_axis_label
        self.initial_plot_title = initial_plot_title
        self.initial_plot_width = plot_width
        self.initial_plot_height = plot_height
        self.data_analysis_function = data_analysis_function
        self.initial_templates = initial_templates
        
        self.initial_plot_types = initial_plot_types
        self.overview_dict_UI_values = {}
        self.overview_dict_objects = {}
        self.widgets = {}
        

        self.items_layout = Layout(flex='1 1 2',
                            width='1')     # override the default width of the button to 'auto' to let the button grow

        box_layout = Layout(display='flex',
                        flex_flow='row wrap',
                        align_items='stretch',
                        border='solid',
                        width='100%',
                        grid_gap='20px 5%')
        
        #first step: choose qcodes db file
        read_from_qcodes = ReadFromQcodes(self)
        self.overview_dict_objects['read_from_qcodes']= read_from_qcodes
        self.box = Box(children=(read_from_qcodes.file_picker,),layout=box_layout)

        self.save_button = widgets.Button(
            description='Save',
            disabled=False,
            button_style='',
        )
        self.widgets['save_button'] = self.save_button
        self.save_button.on_click(self.save_all_ui)

        self.load_button = widgets.Button(
            description='Load from Save',
            disabled=False,
            button_style='',
        )
        self.widgets['load_button'] = self.load_button

        self.load_button.on_click(self.load_all_ui)
        self.update_box()
    
    
    def save_all_ui(self, second_argument_for_technical_reasons):
        '''This function saves all the UI elements to a json file. It is called when the save button is clicked.'''
        with open(r"savedata/file_name.json",'w') as file:
            pickel_dict = jsonpickle.encode(self.overview_dict_UI_values)
            file.write(pickel_dict)
    
    
    def load_all_ui(self, second_argument_for_technical_reasons):
        '''This function loads all the UI elements from a json file. It is called when the load button is clicked.
        It also calls update box with to update the UI elements.
        It works through setting all the UI elements to the values saved in the json file, imitationg a user inputting 
        and choosing what was loaded from file.'''
        with open(r"savedata/file_name.json",'r') as file:
            pickel_dict = file.read()
            self.overview_dict_UI_values = jsonpickle.decode(pickel_dict)
            #print(self.overview_dict_UI_values)
            if 'qcodes_database_name' in self.overview_dict_UI_values:
                path_as_tupel = os.path.split(self.overview_dict_UI_values['qcodes_database_name'])
                self.overview_dict_objects['read_from_qcodes'].file_picker.reset(path=path_as_tupel[0] , filename = path_as_tupel[1] ) 
                database_name = self.overview_dict_UI_values['qcodes_database_name']

                qc.initialise_or_create_database_at(database_name)
                self.list_dataset_names = []
                self.dict_dataset_names_guids = {}
                guids = qc.dataset.guids_from_dbs([database_name])[0][database_name]

                for guid in guids:
                    dataset= qc.dataset.load_by_guid(guid)
                    self.list_dataset_names.append(dataset.name)
                    self.dict_dataset_names_guids[dataset.name] = guid
                
                #choose a dataset
                self.choose_a_dataset = ChooseADataset(self)
                self.overview_dict_objects['choose_a_dataset'] = self.choose_a_dataset
            
                #print('db name:', self.overview_dict_UI_values['qcodes_database_name'])
                if 'dataset_name' in self.overview_dict_UI_values:
                    self.overview_dict_objects['choose_a_dataset'].choose_dataset_dropdown_widget.value = self.overview_dict_UI_values['dataset_name']
                    if 'x_axis' in self.overview_dict_UI_values:
                        self.overview_dict_objects['plot_manager'].choose_x_axis_dropdown_widget.value = self.overview_dict_UI_values['x_axis']
                    if 'y_axis' in self.overview_dict_UI_values:
                        self.overview_dict_objects['plot_manager'].choose_y_axis_dropdown_widget.value = self.overview_dict_UI_values['y_axis']
                        self.overview_dict_objects['plot_manager'].do_plot(1)
                        if 'plot_width' in self.overview_dict_UI_values:
                            self.overview_dict_objects['plot_manager'].plot_width_widget.value = self.overview_dict_UI_values['plot_width']
                        if 'plot_height' in self.overview_dict_UI_values:
                            self.overview_dict_objects['plot_manager'].plot_height_widget.value = self.overview_dict_UI_values['plot_height']
                

    def update_box(self):
        '''This function deletes the current box (meaning the display of all User Input widgets) and 
        creates a new one with the updated UI elements.'''
        clear_output()
        #start fresh on the box.children
        self.box.children = ()
        self.sub_box_general_1 = Box(layout=Layout(display='flex',
                        flex_flow='column',
                        align_items='stretch',
                        border='1px solid black',
                        width='40%'))
        self.sub_box_general_2 = Box(layout=Layout(display='flex',
                        flex_flow='column',
                        align_items='stretch',
                        border='1px solid black',
                        width='40%'))
        
        list_of_general_widgets_1 = ['save_button', 'load_button', 'file_picker', 'choose_dataset_dropdown_widget']                        
        list_of_general_widgets_2 = ['choose_x_axis_dropdown_widget', 'choose_y_axis_dropdown_widget', 'choose_z_axis_dropdown_widget', 'template_dropdown_widget']
        
    
        for widget_name in list_of_general_widgets_1:
            if widget_name in self.widgets.keys():
                self.sub_box_general_1.children = self.sub_box_general_1.children + (self.widgets[widget_name],)
        for widget_name in list_of_general_widgets_2:
        
            if widget_name in self.widgets.keys():
    
                self.sub_box_general_2.children = self.sub_box_general_2.children + (self.widgets[widget_name],)
       
        self.box.children = self.box.children + (self.sub_box_general_1,self.sub_box_general_2)
        
        widgets_in_formated_section = ['file_picker', 'choose_dataset_dropdown_widget', 'choose_x_axis_dropdown_widget', 'choose_y_axis_dropdown_widget', 'choose_z_axis_dropdown_widget', 'save_button', 'load_button', 'plot_type_dropdown_widget', 'plot_color_picker_widget' , 'template_dropdown_widget']
        for widget_name, widget in self.widgets.items():
            if widget_name not in widgets_in_formated_section:
                self.box.children = self.box.children + (widget,)
        
        if 'plot_type_dropdown_widget' in self.widgets.keys():
            #print('plot type dropdown widget found')
            for widget_name, widget in self.widgets['plot_type_dropdown_widget'].items():
                self.box.children = self.box.children + (widget,)

        if 'plot_color_picker_widget' in self.widgets.keys():
            #print('plot color picker widget found')
            #print(self.widgets['plot_color_picker_widget'])
            for widget_name, widget in self.widgets['plot_color_picker_widget'].items():
                self.box.children = self.box.children + (widget,)
            
        display(self.box)
            