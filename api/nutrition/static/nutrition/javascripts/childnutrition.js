function getParam( name )
{
 name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
 var regexS = "[\\?&]"+name+"=([^&#]*)";
 var regex = new RegExp( regexS );
 var results = regex.exec( window.location.href );
 if( results == null )
  return "";
else
 return results[1];
}

Ext.require([
    'Ext.grid.*',
    'Ext.data.*',
    'Ext.panel.*',
    'Ext.toolbar.Paging',
    'Ext.layout.container.Border'
]);

Ext.onReady(function(){

	Ext.define('Province',{
        extend: 'Ext.data.Model',
        fields: ['id','name'],
        proxy: {
            type: 'rest',
            url: '/nutrition/province',

		    reader: {
				type: 'json',
				root: 'records',
				totalProperty: 'count',
				idProperty: 'id'
				}
        }

    });
    
    var province = Ext.create('Ext.data.Store', {
    	pageSize: PAGE_SIZE,
    	storeId: 'province',
    	requires: 'Province',
        model: 'Province',
        root: 'records',
        //autoLoad: true,
    	
        });
    
    Ext.define('District',{
        extend: 'Ext.data.Model',
        fields: ['id','name','province_id'],
        proxy: {
            type: 'rest',
            url: '/nutrition/district',

		    reader: {
				type: 'json',
				root: 'records',
				totalProperty: 'count',
				idProperty: 'id'
				}
        }
    });

    var district = Ext.create('Ext.data.Store', {
    	pageSize: PAGE_SIZE,
    	requires: 'District',
        model: 'District',
        root: 'records',
        //autoLoad: true,
    	
        });
    
    Ext.define('HealthCentre',{
        extend: 'Ext.data.Model',
        fields: ['id','name','province_id'],
        proxy: {
            type: 'rest',
            url: '/nutrition/healthcentre',

		    reader: {
				type: 'json',
				root: 'records',
				totalProperty: 'count',
				idProperty: 'id'
				}
        }
    });

    var healthcentre = Ext.create('Ext.data.Store', {
    	pageSize: PAGE_SIZE,
    	requires: 'HealthCentre',
        model: 'HealthCentre',
        root: 'records',
        //autoLoad: true,
    	
        });

	
	
    Ext.define('ChildNutrition',{
        extend: 'Ext.data.Model',
        fields: ['id','child_number','date_of_birth', {name: 'mother', mapping: 'mother.national_id'},'gender', 'breastfeeding', 'weight', 'height','muac',
                 
                 //{name: 'history', mapping: 'child.history'},
		 //{name: 'village', mapping: 'village'},{name: 'cell', mapping: 'cell.name'},{name: 'sector', mapping: 'sector.name'},
		{name: 'health_centre', mapping: 'health_centre.name'},{name: 'referral_hospital', mapping: 'referral_hospital.name'},
		{name: 'district', mapping: 'district.name'},{name: 'province', mapping: 'province.name'}

		]
    });



    var PAGE_SIZE =50;
    var store = Ext.create('Ext.data.Store', {
	pageSize: PAGE_SIZE,
        model: 'ChildNutrition',
	proxy: {
            type: 'rest',
            url: '/nutrition/cbn'+window.location.search,

	    reader: {
			type: 'json',
			root: 'records',
			totalProperty: 'count',
			idProperty: 'id'
		}
        },
	
    });
    
    var qst = "?";
    if (window.location.search) qst = window.location.search;
    
    var url = window.location.pathname+qst;
	
	var grid = Ext.create('Ext.grid.Panel', {
	store: store,
        title: 'Child Nutrition Report',
	columns: [
            {text: "ID", dataIndex: 'id', sortable: true},
            {text: "Child Number", dataIndex: 'child_number', sortable: true},
	    {text: "Date of Birth", dataIndex: 'date_of_birth', sortable: true},
            {text: "Mother", width: 120, dataIndex: 'mother', sortable: true},
	    {text: "Breastfeeding", dataIndex: 'breastfeeding', sortable: true},
	    {text: "Gender", dataIndex: 'gender', sortable: true},
	    {text: "Weight", dataIndex: 'weight', sortable: true},
	    {text: "Height", dataIndex: 'height', sortable: true},
	    {text: "MUAC", dataIndex: 'muac', sortable: true},
	    //{text: "Village", dataIndex: 'village', sortable: true},
	    //{text: "Cell", dataIndex: 'cell', sortable: true},
	    //{text: "Sector", dataIndex: 'sector', sortable: true},
            {text: "Health Centre", dataIndex: 'health_centre', sortable: true},
	    {text: "Referral Hospital", dataIndex: 'referral_hospital', sortable: true},
	    {text: "District", dataIndex: 'district', sortable: true},
	    {text: "Province", dataIndex: 'province', sortable: true},
	    
	    		
        ],
        tbar:[ /*{
        	xtype:'datefield',
        	id: 'startdate',
        	width:150,
        	fieldLabel:'From',
        	name:'start_date',
        	allowBlank:false,
        	labelWidth: 50,
        	labelStyle:'font-weight:bold;padding-left:10px;width:<X>px;',
        	format: 'd.m.Y', // <------- this way
            editor : {
                xtype : 'datefield',
                format: 'd.m.Y',
                submitFormat: 'c'  // <-------------- this way
            },
        	listeners: {
            	afterrender: function(datefield){
            								if (!getParam('start_date') && datefield.value == null) datefield.setValue( Ext.Date.add (new Date(),Ext.Date.DAY,-1))
            								else if (getParam('start_date')) datefield.setValue(getParam('start_date'))
            								
            								}
              			}
        	},
        	{	
        		xtype:'datefield',
        		id: 'enddate',
            	width:150,
            	fieldLabel:'To',
            	name:'end_date',
            	allowBlank:false,
            	labelWidth: 50,
            	labelStyle:'font-weight:bold;padding-left:10px;width:<X>px;',
            	format: 'd.m.Y', // <------- this way
                editor : {
                    xtype : 'datefield',
                    format: 'd.m.Y',
                    submitFormat: 'c'  // <-------------- this way
                },
            	listeners: {
                	afterrender: function(datefield){
                								if (!getParam('end_date') && datefield.value == null) datefield.setValue( new Date())
                								else if (getParam('end_date')) datefield.setValue(getParam('end_date'))
                								
                								}
                  			}
            	},*/
        	{
				xtype: 'combo',
				width: 150,
				id:'province_combo',
				name: 'province',
				store: province,
				emptyText:'Province',
				displayField: 'name',
				valueField: 'id',
				queryMode: 'local',
				typeAhead:true,
				forceSelection: true,
                minChars: 1,
                listeners: {
                	afterrender: function(combo){
                        combo.store.on('load',function(){
                        	//var recordSelected = combo.getStore().getAt(0);                     
                            //combo.setValue(recordSelected.get('id'));
                        	combo.store.insert(0, Ext.create('Province', {
                                mymodel_id: -1,                  // some invalid id
                                title: 'Choose Province...' // default text for the empty record
                            }));
                        	var match = province.findRecord('id', getParam('province'));
                        	combo.setValue(match.data.id);
                        	district.load({			
	                    		params:{
	                    			province_id:match.data.id	
	                    		}	
	                    	});
                        	healthcentre.load({			
	                    		params:{
	                    			province_id:match.data.id
	                    		}	
	                    	});

                        });
                        },
                    select: function(combo, value, index) {
                    					
					                    	district.load({			
					                    		params:{
					                    			province_id:this.value	
					                    		}	
					                    	});
					                    	healthcentre.load({			
					                    		params:{
					                    			province_id:this.value
					                    		}	
					                    	});
                    				}
                  			}
                  				                  				
		    },
		    ,{
				xtype: 'combo',
				width: 150,
				name: 'district',
				id:'district_combo',
				//disabled: true,
				store: district,
				allowBlank: true,
				displayField: 'name',
				valueField: 'id',
				emptyText:'District',
				queryMode: 'local',
				typeAhead:true,
				forceSelection: true,
                minChars: 1,
                listeners: {
                	afterrender: function(combo){
                        combo.store.on('load',function(){
                        	combo.store.insert(0, Ext.create('District', {
                                mymodel_id: -1,                  // some invalid id
                                title: 'Choose District...' // default text for the empty record
                            }));
                        	var match = district.findRecord('id', getParam('district'));
                        	combo.setValue(match.data.id);
                        	healthcentre.load({			
	                    		params:{
	                    			district_id:match.data.id
	                    		}	
	                    	});

                        });
                        },
                    select: function(combo, value, index) {
					                    	healthcentre.load({			
					                    		params:{
					                    			district_id:this.value	
					                    		}	
					                    	});
                    				}
                  			}
		    }
		    ,{
				xtype: 'combo',
				name: 'healthcentre',
				id:'healthcentre_combo',
				//disabled: true,
				store: healthcentre,
				displayField: 'name',
				valueField: 'id',
				emptyText:'Health Centre',
				queryMode: 'local',
				typeAhead:true,
				forceSelection: true,
                minChars: 1,
                listeners: {
                	afterrender: function(combo){
                        combo.store.on('load',function(){
                        	combo.store.insert(0, Ext.create('HealthCentre', {
                                mymodel_id: -1,                  // some invalid id
                                title: 'Choose Health Centre...' // default text for the empty record
                            }));
                        	var match = healthcentre.findRecord('id', getParam('location'));
                        	combo.setValue(match.data.id);

                        		});
                        	}
                 		}
		    	
		    },
		    {
		    	xtype:'button',
		    	text: '<b>UPDATE FILTERS</b>',
		    	flex:1,
		    	cls: 'buttonT',
		    	listeners:{
		    	click: function() {
		    		
		    		prv = Ext.getCmp('province_combo').value;
		    		dst = Ext.getCmp('district_combo').value;
		    		hc = Ext.getCmp('healthcentre_combo').value;
		    		/*st_date = Ext.getCmp('startdate').value;
		    		e_date = Ext.getCmp('enddate').value;
		    		
		    				    		   		
		    		if (!getParam('start_date') && st_date != null) url = url + "&start_date="+Ext.Date.format(st_date,'d.m.Y');//alert(province[0].value);
		    		else if (getParam('start_date') && st_date != null) url = url.replace("&start_date="+getParam('start_date'),"&start_date="+Ext.Date.format(st_date,'d.m.Y'));
		    		
		    		if (!getParam('end_date') && e_date != null) url = url + "&end_date="+Ext.Date.format(e_date,'d.m.Y');//alert(province[0].value);
		    		else if (getParam('end_date') && e_date != null) url = url.replace("&end_date="+getParam('end_date'),"&end_date="+Ext.Date.format(e_date,'d.m.Y'));
		    		*/
		    		if (!getParam('province') && prv != null) url = url + "&province="+prv;//alert(province[0].value);
		    		else if (getParam('province') && prv != null) url = url.replace("&province="+getParam('province'),"&province="+prv);
		    		else if (prv == null) url = url.replace("&province="+getParam('province'),"");
		    		
		    		if (!getParam('district') && dst != null) url = url + "&district="+dst;//alert(district[0].value);
		    		else if (getParam('district') && dst != null) url = url.replace("&district="+getParam('district'),"&district="+dst);
		    		else if (dst == null) url = url.replace("&district="+getParam('district'),"");
		    		
		    		if (!getParam('location') && hc != null) url = url + "&location="+hc;//alert(healthcentre[0].value);
		    		else if (getParam('location') && hc != null) url = url.replace("&location="+getParam('location'),"&location="+hc);
		    		else if (hc == null) url = url.replace("&location="+getParam('location'),"");
	
					window.location = url;
                    }
		    	}
		    }
                ],

	bbar: Ext.create('Ext.PagingToolbar', {
            store: store,
	    pageSize: PAGE_SIZE,
            displayInfo: true,
            displayMsg: 'Displaying  Children {0} - {1} of {2}',
            emptyMsg: "No Child to display"
        }),
	viewConfig: {
            forceFit: true
        },
        
        region: 'center',
	renderTo: 'childnutrition'
	
    });

      
      store.load({params: {'start': 0, 'limit': PAGE_SIZE}});
   province.load({params: {'start': 0, 'limit': PAGE_SIZE}});
   district.load({params: {'start': 0, 'limit': PAGE_SIZE}});
   healthcentre.load({params: {'start': 0, 'limit': PAGE_SIZE}});
		
});

