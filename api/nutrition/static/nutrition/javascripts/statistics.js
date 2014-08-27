
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

    Ext.define('Statistics',{
        extend: 'Ext.data.Model',
        fields: ['key','desc','total'

		]
    });
    
       
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

    var PAGE_SIZE =10;
    var store = Ext.create('Ext.data.Store', {
	pageSize: PAGE_SIZE,
        model: 'Statistics',
	proxy: {
            type: 'rest',
            url: '/nutrition/stats/data'+window.location.search,

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
    
   // var jsonData = Ext.util.JSON.decode(response.responseText);
    //alert(jsonData.filters);
    
	var grid = Ext.create('Ext.grid.Panel', {
	id: 'statistics',
	store: store,
        title: 'Nutrition Statistics',
	columns: [
            {text: "Indicator", flex: 1,dataIndex: 'desc', sortable: true},
            {text: "Total", dataIndex: 'total', sortable: true},
	    	    
	    		
        ],
        listeners: {      //listener config setting for the grid //itemclick or itemdblclik
    		itemclick: function(dataview, record, item, index, e) {
    			//console.log('dblClick Event')
    			var selection = grid.getSelectionModel().getSelection()
    			window.open(window.location.pathname+'/key/'+selection[0].data.key+qst)
    			//if (!getParam('key')) window.open(url+'&key='+selection[0].data.key)
    			//else if (getParam('key')) window.open(url.replace('&key='+getParam('key'),'&key='+selection[0].data.key))
    		}
    	}
        ,
        tbar:[ {
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
            	},
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
		    		st_date = Ext.getCmp('startdate').value;
		    		e_date = Ext.getCmp('enddate').value;
		    		
		    				    		   		
		    		if (!getParam('start_date') && st_date != null) url = url + "&start_date="+Ext.Date.format(st_date,'d.m.Y');//alert(province[0].value);
		    		else if (getParam('start_date') && st_date != null) url = url.replace("&start_date="+getParam('start_date'),"&start_date="+Ext.Date.format(st_date,'d.m.Y'));
		    		
		    		if (!getParam('end_date') && e_date != null) url = url + "&end_date="+Ext.Date.format(e_date,'d.m.Y');//alert(province[0].value);
		    		else if (getParam('end_date') && e_date != null) url = url.replace("&end_date="+getParam('end_date'),"&end_date="+Ext.Date.format(e_date,'d.m.Y'));
		    		
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
        

	viewConfig: {
            forceFit: true
        },
        
        region: 'center',
	renderTo: 'statistics',
	
    });

	
	   store.load({params: {'start': 0, 'limit': PAGE_SIZE}});
   province.load({params: {'start': 0, 'limit': PAGE_SIZE}});
   district.load({params: {'start': 0, 'limit': PAGE_SIZE}});
   healthcentre.load({params: {'start': 0, 'limit': PAGE_SIZE}});
		
});

