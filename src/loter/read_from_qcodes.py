import qcodes as qc
from pathlib import Path
import xarray as xr
import ipywidgets as widgets
from ipyfilechooser import FileChooser
import matplotlib.pyplot as plt

class ReadFromQcodes():
    '''This class is used to create the widgets for the user to input the name of the database file.'''
    def __init__(self,manager):
        self.manager = manager
        
        self.file_picker = FileChooser()
        self.manager.widgets['file_picker'] = self.file_picker
        self.file_picker.observe(self.process_file_picker,'value')
        self.file_picker.register_callback(self.process_file_picker)

        self.live_update = False
        if self.manager.initial_qcodes_database_name is not None:
            self.database_name = self.manager.initial_qcodes_database_name
            self.manager.overview_dict_UI_values['qcodes_database_name'] = self.database_name
            qc.initialise_or_create_database_at(self.database_name)
            self.manager.list_dataset_names = []
            self.manager.dict_dataset_names_guids = {}
            guids = qc.dataset.guids_from_dbs([self.database_name])[0][self.database_name]

            for guid in guids:
                dataset= qc.dataset.load_by_guid(guid)
                self.manager.list_dataset_names.append(dataset.name)
                self.manager.dict_dataset_names_guids[dataset.name] = guid
            #choose a dataset
            choose_a_dataset = ChooseADataset(self.manager)
            self.manager.overview_dict_objects['choose_a_dataset'] = choose_a_dataset
            
            

    def process_file_picker(self):
        '''This function is called when the user selects a file using the file picker. It updates the database_name and redraws the UI. 
        It creates a new instance of ChooseADataset and adds it to the overview_dict_objects.
        At the moment it also creates a dictionary of xarray datasets from the datasets in the database.'''

        if self.file_picker.selected is not None:
            self.database_name = self.file_picker.selected
            
            self.manager.overview_dict_UI_values['qcodes_database_name'] = self.database_name

            qc.initialise_or_create_database_at(self.database_name)
            self.manager.list_dataset_names = []
            self.manager.dict_dataset_names_guids = {}
            guids = qc.dataset.guids_from_dbs([self.database_name])[0][self.database_name]

            for guid in guids:
                dataset= qc.dataset.load_by_guid(guid)
                self.manager.list_dataset_names.append(dataset.name)
                self.manager.dict_dataset_names_guids[dataset.name] = guid
            
            #choose a dataset
            self.choose_a_dataset = ChooseADataset(self.manager)
            self.manager.overview_dict_objects['choose_a_dataset'] = self.choose_a_dataset
            self.manager.update_box()

            
class ChooseADataset():
    '''This class is used to create the widgets for the user to choose a dataset from the database.'''
    def __init__(self, manager):
        self.manager = manager

        self.choose_dataset_dropdown_widget = widgets.Dropdown(
            options = self.manager.list_dataset_names,
            description='Choose a dataset:',
            disabled=False,
            style= {'description_width': 'initial'}
        )
        self.manager.widgets['choose_dataset_dropdown_widget'] = self.choose_dataset_dropdown_widget
        #print(self.manager.widgets)
        self.choose_dataset_dropdown_widget.observe(self.process_choose_dataset_dropdown_widget,'value')

        if self.manager.initial_dataset_name is not None:
            self.dataset_name = self.manager.initial_dataset_name
            self.manager.overview_dict_UI_values['dataset_name'] = self.dataset_name
            self.manager.overview_dict_objects['plot_manager'] = PlotManager(self.manager)
            self.manager.overview_dict_objects['template_manager'] = TemplateManager(self.manager)

    def process_choose_dataset_dropdown_widget(self,change):
        '''This function is called when the user selects a dataset from the dropdown. It updates the dataset_name and redraws the UI. 
        It creates a new instance of PlotManager and adds it to the overview_dict_objects.'''
        self.dataset_name = change.new
        self.manager.overview_dict_UI_values['dataset_name'] = self.dataset_name
        self.manager.overview_dict_objects['plot_manager'] = PlotManager(self.manager)
        self.manager.overview_dict_objects['template_manager'] = TemplateManager(self.manager)
        

class PlotManager():
    '''This class manages everyhing related to plotting the data from the dataset.
    It creates the widgets for the user to choose the x and y axes and the visual aspects of the plot.'''
    def __init__(self, manager):
        # try to set the backend to ipympl
        try:
            import matplotlib
            matplotlib.use('module://ipympl.backend_nbagg')
        except:
            pass
        self.manager = manager
        self.x_axis = None
        #print(self.manager.overview_dict_UI_values['dataset_name'])
        self.dataset = qc.load_by_guid(self.manager.dict_dataset_names_guids[self.manager.overview_dict_UI_values['dataset_name']])
        # If analysis functions should be applied to the data, that should happen here. I should get a datset as an input and return a dataset as an output.
        # The program will then use the output dataset for all following operations.
        # writing a good data analysis function will in most cases require an understanding of the specific dataset the function will be applied to.
        if self.manager.data_analysis_function is not None:
            self.dataset = self.manager.data_analysis_function(self.dataset)


        self.parameter_names = []

        for parameter in self.dataset.get_parameters():
            self.parameter_names.append(parameter.name)

        self.choose_x_axis_dropdown_widget = widgets.Dropdown(
            options = self.parameter_names,
            description = 'Choose x axis:',
            disabled = False,
            layout = self.manager.items_layout,
            style = {'description_width': 'initial'}
        )
        self.manager.widgets['choose_x_axis_dropdown_widget'] = self.choose_x_axis_dropdown_widget
        self.choose_x_axis_dropdown_widget.observe(self.process_choose_x_axis_dropdown_widget,'value')
       
        
        self.y_axis = None
        self.choose_y_axis_dropdown_widget = widgets.SelectMultiple(
            options = self.parameter_names,
            description = 'Choose y axis:',
            disabled = False,
            layout = self.manager.items_layout,
            style = {'description_width': 'initial'}
        )
        self.manager.widgets['choose_y_axis_dropdown_widget'] = self.choose_y_axis_dropdown_widget
        self.choose_y_axis_dropdown_widget.observe(self.process_choose_y_axis_dropdown_widget,'value')
        

        self.z_axis = None
        self.choose_z_axis_dropdown_widget = widgets.Dropdown(
            options = self.parameter_names,
            description = 'Choose z axis (for pcolormesh plot):',
            disabled = False,
            layout = self.manager.items_layout,
            style = {'description_width': 'initial'}
        )
        self.manager.widgets['choose_z_axis_dropdown_widget'] = self.choose_z_axis_dropdown_widget
        self.choose_z_axis_dropdown_widget.observe(self.process_choose_z_axis_dropdown_widget,'value')
      

        self.x_axis_label = widgets.Text(
            value = 'x axis',
            description = 'x axis label',
            continuous_update = False,
            style = {'description_width': 'initial'}
        )
        self.x_axis_label.observe(self.process_x_axis_label,'value')

        self.y_axis_label = widgets.Text(
            value = 'y axis',
            description = 'y axis label',
            continuous_update = False,
            style = {'description_width': 'initial'}
        )
        self.y_axis_label.observe(self.process_y_axis_label,'value')

        self.plot_title = widgets.Text(
            value = 'plot title',
            description = 'plot title',
            continuous_update = False,
            style = {'description_width': 'initial'}
        )
        self.plot_title.observe(self.process_plot_title,'value')

        self.plot_width_widget = widgets.BoundedFloatText(
            value = 7.5,
            min = 1,
            max = 20.0,
            step = 0.1,
            description = 'plot width:',
            disabled = False,
            style = {'description_width': 'initial'}
        )
        self.plot_width_widget.observe(self.process_plot_width,'value')

        self.plot_height_widget = widgets.BoundedFloatText(
            value = 7.5,
            min = 1,
            max = 20.0,
            step = 0.1,
            description = 'plot height:',
            disabled = False,
            style = {'description_width': 'initial'}
        )
        self.plot_height_widget.observe(self.process_plot_height,'value')

        self.plot_button = widgets.Button(description='Plot')
        self.manager.widgets['plot_button'] = self.plot_button
        self.plot_button.on_click(self.do_plot)

        self.manager.update_box()
        
       
        if self.manager.overview_dict_UI_values.get('plot_type') is None:
                self.manager.overview_dict_UI_values['plot_type'] = {}
        if self.manager.overview_dict_objects.get('plot_type') is None:
                self.manager.overview_dict_objects['plot_type'] = {}
        for one_y_axis in self.parameter_names:
            if self.manager.overview_dict_UI_values.get('plot_type',{}).get(one_y_axis) is None:
                self.manager.overview_dict_UI_values['plot_type'][one_y_axis] = 'scatter'
            if self.manager.overview_dict_objects.get('plot_type',{}).get(one_y_axis) is None:
                self.manager.overview_dict_objects['plot_type'][one_y_axis] = PlotType(self.manager, one_y_axis)

        if self.manager.initial_x_axis is not None:
            self.x_axis = self.manager.initial_x_axis
            self.manager.overview_dict_UI_values['x_axis'] = self.x_axis
        
        if self.manager.initial_y_axis is not None:
            self.y_axis = self.manager.initial_y_axis
            self.manager.overview_dict_UI_values['y_axis'] = self.y_axis
        
        if self.manager.initial_z_axis is not None:
            self.z_axis = self.manager.initial_z_axis
            self.manager.overview_dict_UI_values['z_axis'] = self.z_axis
        
        self.manager.widgets['plot_type_dropdown_widget'] = {}
        if self.manager.initial_y_axis is not None:
            self.y_axis = self.manager.initial_y_axis
            self.manager.overview_dict_UI_values['y_axis'] = self.y_axis
            for one_y_axis in self.y_axis:
                self.manager.widgets['plot_type_dropdown_widget'][one_y_axis] = self.manager.overview_dict_objects['plot_type'][one_y_axis].plot_type_dropdown_widget



    def process_choose_x_axis_dropdown_widget(self,change):
        '''This function is called when the user selects data to go on the x axis. It updates the x_axis.'''
        self.x_axis = change.new
        self.manager.overview_dict_UI_values['x_axis'] = self.x_axis
    
    def process_choose_z_axis_dropdown_widget(self,change):
        '''This function is called when the user selects data to go on the z axis. It updates the z_axis.'''
        self.z_axis = change.new
        self.manager.overview_dict_UI_values['z_axis'] = self.z_axis

    def process_choose_y_axis_dropdown_widget(self,change):
        '''This function is called when the user selects data to go on the y axis. It updates the y_axis and potentially draws an additional line.'''
        self.y_axis = change.new
        self.manager.overview_dict_UI_values['y_axis'] = self.y_axis
        # have to delete all the plot_type widgets off the widget list here since we do not want widgets belonging to y axis that are not selected to be shown
        # the plot_type widgets are still in the overview_dict_objects and can be added to the widget list again if the y axis is selected again 
        self.manager.widgets['plot_type_dropdown_widget'] = {}
        for one_y_axis in self.y_axis:
            # add the plot_type widgets to the widget list again
            self.manager.widgets['plot_type_dropdown_widget'][one_y_axis] = self.manager.overview_dict_objects['plot_type'][one_y_axis].plot_type_dropdown_widget
                

    def do_plot(self,second_argument_for_technical_reasons):
        '''This function is called when the user clicks the plot button. It creates a matplotlib plot instance and adds it to the overview_dict_objects.'''
        if self.manager.overview_dict_objects.get('plot') is not None:
            plt.close(self.manager.overview_dict_objects['plot'])
        self.fig, self.ax = plt.subplots()
        self.manager.overview_dict_objects['plot'] = self.fig

        if self.manager.initial_x_axis_label is not None:
            self.ax.set_xlabel(self.manager.initial_x_axis_label)
            self.manager.overview_dict_UI_values['x_axis_label'] = self.manager.initial_x_axis_label
        else:
            self.ax.set_xlabel(self.x_axis)
        
        if self.manager.initial_y_axis_label is not None:
            self.ax.set_ylabel(self.manager.initial_y_axis_label)
            self.manager.overview_dict_UI_values['y_axis_label'] = self.manager.initial_y_axis_label
        else:
            self.ax.set_ylabel(self.y_axis)
        
        if self.manager.initial_plot_title is not None:
            self.ax.set_title(self.manager.initial_plot_title)
            self.manager.overview_dict_UI_values['plot_title'] = self.manager.initial_plot_title
        if self.manager.initial_plot_width is not None:
            self.fig.set_figwidth(self.manager.initial_plot_width)
            self.manager.overview_dict_UI_values['plot_width'] = self.manager.initial_plot_width
        if self.manager.initial_plot_height is not None:
            self.fig.set_figheight(self.manager.initial_plot_height)
            self.manager.overview_dict_UI_values['plot_height'] = self.manager.initial_plot_height
        
        self.manager.widgets['x_axis_label'] = self.x_axis_label
        self.manager.widgets['y_axis_label'] = self.y_axis_label
        self.manager.widgets['plot_title'] = self.plot_title
        self.manager.widgets['plot_width_widget'] = self.plot_width_widget
        self.manager.widgets['plot_height_widget'] = self.plot_height_widget
        

        temp_x = self.dataset.get_parameter_data(self.x_axis)[self.x_axis][self.x_axis]
        if self.manager.overview_dict_UI_values.get('z_axis') is not None:
            temp_z = self.dataset.get_parameter_data(self.z_axis)[self.z_axis][self.z_axis]
            if len(self.y_axis) == 1:
                temp_y = self.dataset.get_parameter_data(self.y_axis[0])[self.y_axis[0]][self.y_axis[0]]
                try:
                    self.ax.pcolormesh(temp_x,temp_y,temp_z)
                    self.ax.set_xlabel(self.x_axis)
                    self.ax.set_ylabel(self.y_axis[0])
                    self.manager.update_box()
                    plt.show()
                except:
                    print("these axes are not compatible for a matplotlib pcolormesh plot.")
            else:
                print('z axis is for now only implemented for one y axis')
        else:
        #empty the color picker widget list, it will be filles with new widgets in the next loop
            self.manager.widgets['plot_color_picker_widget'] = {}
            for one_y_axis in self.y_axis:
                temp_y = self.dataset.get_parameter_data(one_y_axis)[one_y_axis][one_y_axis]
                #print('temp_y',temp_y.shape)
                if self.manager.overview_dict_objects.get('plot_color') is None:
                    self.manager.overview_dict_objects['plot_color'] = {}
                if self.manager.overview_dict_objects.get('plot_color',{}).get(one_y_axis) is None:
                    self.manager.overview_dict_objects['plot_color'][one_y_axis] = PlotColor(self.manager, one_y_axis)
                self.manager.widgets['plot_color_picker_widget'][one_y_axis] = self.manager.overview_dict_objects['plot_color'][one_y_axis].plot_color_picker_widget
                if len(temp_x) == len(temp_y):
                    if self.manager.overview_dict_UI_values.get('plot_type',{}).get(one_y_axis) is None:
                        if self.manager.overview_dict_UI_values.get('plot_color',{}).get(one_y_axis) is not None:
                            self.ax.scatter(temp_x,temp_y, label=one_y_axis, color=self.manager.overview_dict_UI_values['plot_color'][one_y_axis])
                        else:
                            self.ax.scatter(temp_x,temp_y, label=one_y_axis)
                    elif self.manager.overview_dict_UI_values['plot_type'][one_y_axis] == 'scatter':
                        if self.manager.overview_dict_UI_values.get('plot_color',{}).get(one_y_axis) is not None:
                            self.ax.scatter(temp_x,temp_y, label=one_y_axis, color=self.manager.overview_dict_UI_values['plot_color'][one_y_axis])
                        else:
                            self.ax.scatter(temp_x,temp_y, label=one_y_axis)
                    elif  self.manager.overview_dict_UI_values['plot_type'][one_y_axis] == 'line':
                        if self.manager.overview_dict_UI_values.get('plot_color',{}).get(one_y_axis) is not None:
                            self.ax.plot(temp_x,temp_y, label=one_y_axis, color=self.manager.overview_dict_UI_values['plot_color'][one_y_axis])
                        else:
                            self.ax.plot(temp_x,temp_y, label=one_y_axis)
                    self.ax.legend()
                    self.manager.update_box()
                    plt.show()
                else:
                    print('x and y are not the same length') 
    
    def update_plot(self):
        '''This function is called when the subplot needs to be redrawn becourse the plot type or something similarly fundamental has been updated.'''
        self.ax.cla()
        if self.manager.overview_dict_UI_values.get('x_axis_label') is not None:
            self.ax.set_xlabel(self.manager.overview_dict_UI_values['x_axis_label'])
        if self.manager.overview_dict_UI_values.get('y_axis_label') is not None:
            self.ax.set_ylabel(self.manager.overview_dict_UI_values['y_axis_label'])
        if self.manager.overview_dict_UI_values.get('plot_title') is not None:
            self.ax.set_title(self.manager.overview_dict_UI_values['plot_title'])
        temp_x = self.dataset.get_parameter_data(self.x_axis)[self.x_axis][self.x_axis]
        for one_y_axis in self.y_axis:
            temp_y = self.dataset.get_parameter_data(one_y_axis)[one_y_axis][one_y_axis]
            if len(temp_x) == len(temp_y):
                if self.manager.overview_dict_UI_values.get('plot_type',{}).get(one_y_axis) is None:
                    if self.manager.overview_dict_UI_values.get('plot_color',{}).get(one_y_axis) is not None:
                        self.ax.scatter(temp_x,temp_y, label=one_y_axis, color=self.manager.overview_dict_UI_values['plot_color'][one_y_axis])
                    else:
                        self.ax.scatter(temp_x,temp_y, label=one_y_axis)
                else:
                    if self.manager.overview_dict_UI_values['plot_type'][one_y_axis]  == 'scatter':
                        if self.manager.overview_dict_UI_values.get('plot_color',{}).get(one_y_axis) is not None:
                            self.ax.scatter(temp_x,temp_y, label=one_y_axis, color=self.manager.overview_dict_UI_values['plot_color'][one_y_axis])
                        else:
                            self.ax.scatter(temp_x,temp_y, label=one_y_axis)
                    elif self.manager.overview_dict_UI_values['plot_type'][one_y_axis]  == 'line':
                        if self.manager.overview_dict_UI_values.get('plot_color',{}).get(one_y_axis) is not None:
                            self.ax.plot(temp_x,temp_y, label=one_y_axis, color=self.manager.overview_dict_UI_values['plot_color'][one_y_axis])
                        else:
                            self.ax.plot(temp_x,temp_y, label=one_y_axis)
                self.ax.legend()
            else:
                print('x and y are not the same length')
        
        

        
    def process_x_axis_label(self,change):
        '''This function is called when the user changes the x axis label. It updates the x axis label.'''
        self.ax.set_xlabel(change.new)
        self.manager.overview_dict_UI_values['x_axis_label'] = change.new
        self.fig.canvas.draw()

    def process_y_axis_label(self,change):
        '''This function is called when the user changes the y axis label. It updates the y axis label.'''
        self.ax.set_ylabel(change.new)
        self.manager.overview_dict_UI_values['y_axis_label'] = change.new
        self.fig.canvas.draw()

    def process_plot_title(self,change):
        '''This function is called when the user changes the plot title. It updates the plot title.'''
        self.ax.set_title(change.new)
        self.manager.overview_dict_UI_values['plot_title'] = change.new
        self.fig.canvas.draw()

    def process_plot_width(self,change):
        '''This function is called when the user changes the plot width. It updates the plot width.'''
        self.fig.set_figwidth(change.new)
        self.manager.overview_dict_UI_values['plot_width'] = change.new
        self.fig.canvas.draw()

    def process_plot_height(self,change):
        '''This function is called when the user changes the plot height. It updates the plot height.'''
        self.fig.set_figheight(change.new)
        self.manager.overview_dict_UI_values['plot_height'] = change.new
        self.fig.canvas.draw()

class PlotType():
    '''This class is used to create the widgets for the user to choose the type of plot to be drawn. There is one PlotType instance for each chosen y axis data.'''
    def __init__(self,manager, y_axis_name):
        self.manager = manager
        self.y_axis_name = y_axis_name
        self.plot_type_dropdown_widget = widgets.Dropdown(
            options = ['scatter','line'],
            description = 'plot type ' + self.y_axis_name,
            disabled = False,
            style = {'description_width': 'initial'}
        )
        self.plot_type_dropdown_widget.observe(self.process_plot_type_dropdown_widget,'value')

    def process_plot_type_dropdown_widget(self,change):
        '''This function is called when the user selects a plot type. It updates the plot type and makes the plot be redrawn.'''
        if self.manager.overview_dict_UI_values.get('plot_type') is None:
            self.manager.overview_dict_UI_values['plot_type'] = {}
        self.manager.overview_dict_UI_values['plot_type'][self.y_axis_name] = change.new
        self.manager.overview_dict_objects['plot_type'][self.y_axis_name] = change.new
        if hasattr(self.manager.overview_dict_objects.get('plot_manager') , 'fig'):
            self.manager.overview_dict_objects['plot_manager'].update_plot()
       
class PlotColor():
    '''This class is used to create the widgets for the user to choose the color of the lines or dots in the plot. 
    There is one PlotColor instance for each chosen y axis data.'''
    def __init__(self,manager, y_axis_name):
        self.manager = manager
        self.y_axis_name = y_axis_name
        self.plot_color_picker_widget = widgets.ColorPicker(
            concise = False,
            description = 'color ' + self.y_axis_name,
            style = {'description_width': 'initial'}
        )
        self.plot_color_picker_widget.observe(self.process_plot_color_picker_widget,'value')

    def process_plot_color_picker_widget(self,change):
        '''This function is called when the user selects a color. It updates the color and makes the plot be redrawn.'''
        if self.manager.overview_dict_UI_values.get('plot_color') is None:
            self.manager.overview_dict_UI_values['plot_color'] = {}
        self.manager.overview_dict_UI_values['plot_color'][self.y_axis_name] = change.new
        if hasattr(self.manager.overview_dict_objects.get('plot_manager') , 'fig'):
            self.manager.overview_dict_objects['plot_manager'].update_plot()

        
class TemplateManager():
    '''This class is used to create the widgets for the user to choose a template. It also will if a template is choosen update plot and ui to refelct the template. 
    It works similar to load from save but with a potental gaps in the load from save data. It also assumes, that a qcodes database is already chosen.'''  

    def __init__(self,manager):
        self.manager = manager
        self.template_dropdown_widget = widgets.Dropdown(
            options = ['none', 'all_green' , 'plot_all' ],
            description='Choose a template:',
            disabled=False,
            style= {'description_width': 'initial'}
        )
        self.manager.widgets['template_dropdown_widget'] = self.template_dropdown_widget
        #print("template_dropdown_widget")
        self.template_dropdown_widget.observe(self.process_template_dropdown_widget,'value')
        self.template_names_functions_dict = {'none':self.none, 'all_green':self.all_green, 'plot_all':self.plot_all}
        if self.manager.initial_templates is not None:
            for template in self.manager.initial_templates:
                if self.template_names_functions_dict.get(template) is not None:
                    self.template_names_functions_dict[template](self.manager)
                    self.active_template = template       
                    #print('i did a template')

    def process_template_dropdown_widget(self,change):
        '''This function is called when the user selects a template. It updates the template and calls the appropriate template function.'''
        self.active_template = change.new
        self.manager.overview_dict_UI_values['active_template'] = self.active_template
        self.template_names_functions_dict[self.active_template](self.manager)

    def all_green(self,manager):
        '''This function is called when the user selects the all green template. It changes all colors in the plot to green.
        This is not ment to be usefull but to show how a template function could look.'''
        if manager.overview_dict_UI_values.get('plot_color') is None:
            manager.overview_dict_UI_values['plot_color'] = {}
        for possible_y_axis in manager.overview_dict_objects['plot_manager'].parameter_names:
            manager.overview_dict_UI_values['plot_color'][possible_y_axis] = 'green' 
        if hasattr(manager.overview_dict_objects.get('plot_manager') , 'fig'):
            manager.overview_dict_objects['plot_manager'].update_plot()
        else:
            print('i am not being updated')

    def plot_all(self,manager):
        '''This function is called when the user selects the plot all template. It makes all data be plotted as lines.'''
        if manager.overview_dict_UI_values.get('plot_type') is None:
            manager.overview_dict_UI_values['plot_type'] = {}
        for possible_y_axis in manager.overview_dict_objects['plot_manager'].parameter_names:
            manager.overview_dict_UI_values['plot_type'][possible_y_axis] = 'line'
        manager.overview_dict_objects['plot_manager'].y_axis = manager.overview_dict_objects['plot_manager'].parameter_names
        manager.overview_dict_UI_values['y_axis'] = manager.overview_dict_objects['plot_manager'].parameter_names
        if hasattr(manager.overview_dict_objects.get('plot_manager') , 'fig'):
            manager.overview_dict_objects['plot_manager'].update_plot()
        elif hasattr(manager.overview_dict_objects.get('plot_manager') , 'x_axis'):
            manager.overview_dict_objects['plot_manager'].do_plot('dummy argument')

    def none(self,manager):
        pass