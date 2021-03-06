//constants:
var VIEW_WIDTH=1400;
var VIEW_HEIGHT=800;

//This module must contain:

function makeBetViewButton(bayesVar)
{
    var betViewButton=makeTextWidget("BETS", 15, "Arial", "#666");
    var callback ={
	bayesVar:bayesVar,
	call: function()
	{
	    //this function must kill the current active view if there is one:
	    if (this.bayesVar.hasAcativeView===true)
		//bayesVar.activeView can be bayesVar.betView, bayesVar.modelView, or bayesVar.dataView,
		//these are added whith bayesVar.probSetter as properties of the bayesVar. 
	    {
		this.bayesVar.activeView.erase();
		this.bayesVar.hasActiveView=false;
	    }
	    this.bayesVar.activeView=bayesVar.betView;
	    this.bayesVar.hasActiveView=true;
	    //note that just as every bayesVar has a probSetter
	    //every bayesVar has to have a betView from the beginning
	    //which can be visible or not, but it always exists.
	    this.bayesVar.activeView.render(stage, Point(100, 70));
	    //next, it must make MODEL and DATA buttons and render them.
	    //But these buttons should be part of the bayesVar.betView. 
	    //note that it also must not turn it self off 
	    //as this button automatically disapears when the other active
	    //views are killed (it only exists as part of the model and the 
	    //data views. 
	}
    
    }
    makeClickable2(betViewButton, callback);
    return betViewButton;
    //this betViewButton is to be included in each variable's 
    //MODEL and DATA views. 
}

//instead of makeDoneButton, we double click on the blackFade object, which is evoked ONLY when someone double-clicks on a bayesCircle object. However, we still need a minimization button. The click-out can be simplified a great deal, because all we need to do is to know which bayesVar is the current one (blackFade.currentOne) and then we must just do the following: 
function makeBlackFade() 
{
    var blackFade = WidgetHL();
    blackFade.background = makeRect(stageWidth, stageHeight, "rgba(0, 0, 0, 0.75)");
    blackFade.background.render(blackFade.shape, {x:0, y:0}); //rendering should happen after makeBlackFade is called

    blackFade.on("dblclick", function (evt)
		 {
		     //this.currentOne must be a bayesVar with an activeView, 
		     //which is attached to the blackFade (this).
		     this.currentOne.activeView.erase()
		     this.currentOne.hasActiveView=false;  
		     this.erase()
		 });

    return blackFade
		 
}
//also, blackFade must keep free the area where the buttons are (which is part of the activeViews), because otherwise it will be too easy to exidentally hit the blackFade when people try to click on the buttons. 
//interestingly this should allow to later render it again--so that if the same variable is double-clicked again, it renders the same activeView again, erase just unrenders it but the activeView is still there (although the value of hasActiveView is false). The default active view is bayesVar.modelView, which renders bayesVar.propSetter as part of it.   

function bayesVarFactory ()
{
    var colors = ["#3B4DD0",  "yellow", "red", "green", "purple", "brown",
                  "DarkRed", "GoldenRod"];
    var BayesVar = {};
    var numVars = 0;
    var makeBayesVar = function(varName, varText, possibilities )
    {
        var newBayesVar = Object.create(BayesVar);
        newBayesVar.color = colors[numVars];
        newBayesVar.varName = varName;
        newBayesVar.varText = varText;
        newBayesVar.possibilities = possibilities;
	newBayesVar.activeCircles=[]
        newBayesVar.varCircles = [];
        newBayesVar.isMultiVar = false;
        newBayesVar.probSetter = makeHist([20, 30, 50], possibilities,
                                  700, 400, 20, newBayesVar.color);
	newBayesVar.hasActiveView=false;
	//this is where all the views are added to each bayesVar:
	newBayesVar.betView=makeBettingView(VIEW_WIDTH, VIEW_HEIGHT, newBayesVar);
	newBayesVar.betView.shape.scaleX = 0.5;
	newBayesVar.betView.shape.scaleY = 0.5;
	//rendering occurs in the buttons.
	//Similarly, below should be newBayesVar.modelView and newBayesVar.dataView.
	

        numVars += 1;

        newBayesVar.addCircle = function ()
        {
            var newVarCircle = makeBayesCircle(20, this.color);
            newVarCircle.bayesVar = this;

            newVarCircle.makeMiniHist = function(vals) 
            { 
                this.miniHistShown = false;
                this.miniHist = makeHist(vals, 
					 this.bayesVar.possibilities,
					 700, 400, 20, this.bayesVar.color);
                this.miniHist.killButton = makeTextWidget("x", 60, "Arial", "#f0f0f0");
        /*Now I'm creating the kill switch that allows erasing the little histogram */
                this.miniHist.killButton.miniHist=this.miniHist;
                this.miniHist.killButton.bayesCircle=this;
                this.miniHist.killButton.call = function() 
		{
                    if (this.bayesCircle.miniHistShown)
                    {
                        stage.removeChild(this.miniHist.shape)
                    }
                }
                this.miniHist.killButton.render(this.miniHist.shape, {x:10, y:0});
		
                this.miniHist.shape.on("mouseover", function(evt)
				       {
					   this.widget.killButton.changeColor("#666");
					   /*Actual interaction with the button*/
					   this.widget.killButton.shape.on("mouseover", function(evt)
									   {
									       this.widget.changeColor("red");
									       this.widget.changeFont("120px " + "Arial");
									   });
					   this.widget.killButton.shape.on("mouseout", function(evt)
									   {
									       this.widget.changeColor("#666");
									       this.widget.changeFont("60px " + "Arial");
									   });
					   this.widget.killButton.shape.on("mousedown", function(evt)
									   {
									       this.widget.changeColor("red");
									       this.widget.changeFont("120px " + "Arial");
									       mousePressed = true;
									   });
					   this.widget.killButton.shape.on("pressup", function(evt)
									   {
									       this.widget.changeColor("red");
									       this.widget.changeFont("240px " + "Arial");
									       this.widget.call();
									   });
				       });
                this.miniHist.shape.on("mouseout", function(evt)
				       {
					   this.widget.killButton.changeColor("#f0f0f0");
				       });
                this.miniHist.shape.scaleX = 0.2;
                this.miniHist.shape.scaleY = 0.2;
                this.miniHist.offset = {x:-30, y:30};
                this.miniHist.isMini = true;
                if (this.bayesVar.isMultiVar)
                {
                    this.miniHist.bigHist = this.bayesVar.probSetter.getCurrHist();
                } 
		else 
		{
                    this.miniHist.bigHist = this.bayesVar.probSetter;
                }
                this.miniHist.bigHist.smallHists.push(this.miniHist);
                return this.miniHist;
            }

            newVarCircle.showMiniHist = function()
            {
                this.miniHistShown = true;
                var histX = this.shape.x+this.miniHist.offset.x;
                var histY = this.shape.y+this.miniHist.offset.y;
                this.miniHist.render(stage, Point(histX, histY));
            }

            newVarCircle.makeMiniHist([20, 30, 50]);

            var circleShape = newVarCircle.shape;

            circleShape.on("mousedown", function (evt) 
			   {
			       var globalPt = this.parent.localToGlobal(this.x, this.y);
			       //each new coordinate (globalPt) should be recorded to MongoDB.
			       this.parent.removeChild(this);
			       this.widget.render(stage, {x:globalPt.x, y:globalPt.y});
			       stage.addChild(this);
		 	       this.widget.bayesVar.activeCircles.push(this.widget)
			       this.widget.justAdded = true;
		           }, null, true);

            circleShape.on("dblclick", function (evt)
			   {
			       var varText = this.widget.bayesVar.varText;
			       tutorial.trigger("circleDblClicked", varText);
			       var blackFade = makeBlackFade();
			       blackFade.currentOne = this.widget.bayesVar;
			       blackFade.render(stage, {x:0, y:0});
			       //the default activeView should be modelView.
			       this.widget.bayesVar.activeView.render(stage, {x:100, y:55});
			       this.widget.bayesVar.hasActiveView=true;

			       //the below code is commented out because these objects now belong to the views:
			       //var dataSwitch = makeTextWidget("DATA", 15, "Arial", "#666");
			       //dataSwitch.render(stage, {x:100, y:55});

			       //var modelSwitch = makeTextWidget("MODEL", 15, "Arial", "#ffffff");
			       //modelSwitch.render(stage, {x:150, y:55});
		
			       //var bettingSwitch=makeBetViewButton(this.widget.bayesVar);
			       //bettingSwitch.render(stage, {x:215, y:55});
                
			       var sideBar = this.widget.bayesVar.sideBar;

			       var theOne = this.widget.bayesVar;
		
			       sideBar.show = function()
			       {
				   for (var i=0; i< sideBar.Vars.length; i++)
				   {
				       var variable=sideBar.Vars[i];
                        
				       if (variable === theOne)
				       {
					   variable.varBarItem2.isActive=false;
					   variable.varBarItem2.text.changeColor("#ffffff");
					   variable.varBarItem2.varBarButton.changeColor(variable.color);
					   variable.varBarItem2.varBarButton.renderW(variable.varBarItem2, {x:30, y:20});
					   variable.varBarItem2.text.renderW(variable.varBarItem2, {x:0, y:0});
					   variable.varBarItem2.render(stage, {x:5, y:sideBar.Vars[i].varBarItem2.place});
                        	       }
				       else
				       {
					   variable.varBarItem2.text.changeColor("rgba(0, 0, 0, 0.01)");

					   variable.varBarItem2.varBarButton.changeColor("rgba(0, 0, 0, 0.01)");
					   variable.varBarItem2.varBarButton.renderW(variable.varBarItem2, {x:30, y:20});
					   variable.varBarItem2.text.renderW(variable.varBarItem2, {x:0, y:0});
					   variable.varBarItem2.render(stage, {x:5, y:sideBar.Vars[i].varBarItem2.place})
				       }
				   }
			       }
			       /*closing it all out again*/

			       sideBar.back = function(miniHist)
			       {
				   for (var i=0; i< this.Vars.length; i++)
				   {
				       var variable=this.Vars[i];
				       variable.varBarItem2.erase();
				       if (variable.hasActiveView)
				       {
					   variable.activeView.erase();
					   variable.hasActiveView=false;
				       }
				       if (!variable.varBarItem2.isActive)
				       {
					   if (miniHist)
					   {
					       variable.activeCircles[0].showMiniHist();
					   }
					   else 
					   {
					       if (variable.activeCircles[0].miniHistShown)
					       {
						   stage.removeChild(variable.activeCircles[0].miniHist.shape)
					       }
					   }
					   variable.varBarItem2.isActive=true;
				       };
				   }
			       }

			       sideBar.show();
                
                
			       //theOne.hasActiveView = true;
			       //theOne.activeView = theOne.probSetter;
			       //theOne.activeView.render(stage, {x:100, y:70});
			       //var closingSocket = WidgetHL();
			       //closingSocket.doneButton = makeDoneButton(theOne.activeView, 
				//					 this.widget, stage, blackFade, dataSwitch,
				//					 modelSwitch, bettingSwitch, closingSocket, sideBar);

			       //closingSocket.reduceButton = makeDoneButton(theOne.activeView, 
				//					   this.widget, stage, blackFade,  dataSwitch,
				//					   modelSwitch, bettingSwitch, closingSocket, sideBar);

			       //closingSocket.doneButton.closingSocket=closingSocket;
			       //closingSocket.reduceButton.closingSocket=closingSocket;

			       //closingSocket.reduceButton.miniHist=true;
			       //closingSocket.reduceButton.changeText("-");
			       //closingSocket.reduceButton.changeFont("150px Courier")
			       //closingSocket.doneButton.renderW(closingSocket, {x:0, y:-15});
			       //closingSocket.reduceButton.renderW(closingSocket, {x:-5, y:-60});

			      // closingSocket.render(stage, {x: 5, y: 4});
                    
			   });

                   
            this.varCircles.push(newVarCircle)
            return newVarCircle;
        }

        newBayesVar.removeCircle = function (varCircle)
        {
            newBayesVar.varCircles.deleteFirstElem(varCircle);
        }

        
        newBayesVar.getFromVars = function ()
        {
            var fromVars = Set();
            for (var i=0;i<this.varCircles.length;i++)
            {
                for (var j=0;j<this.varCircles[i].fromNodes.length;j++)
                {
                    var fromVar = this.varCircles[i].fromNodes[j][0].bayesVar;
                    fromVars.add(fromVar);
                }
            }
            return fromVars.itemList;
        }

        newBayesVar.getMenuChoices = function ()
        {
            var menuChoices = Set();
            var fromVars = this.getFromVars();
            for (var i=0;i<fromVars.length;i++)
            {
                menuChoices.add(fromVars[i].varName);
                for (var j=0;j<fromVars[i].possibilities.length;j++)
                {
                    menuChoices.add(fromVars[i].possibilities[j]);
                }
            }
            return menuChoices;
        }
        return newBayesVar;
    }
    return makeBayesVar;
}

 
 
