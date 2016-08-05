var debug=0;
var indexSelected=0;

var localhost="localhost";
var dbroot="http://"+localhost+"/interact/php/interact.php";
var myOrigin={appName:"QCSurf"};
var myIP;

var W;
var H;
var container;
var overlay;
var camera, scene, renderer, trackball;
var mesh;
var materials = [
    new THREE.MeshNormalMaterial(),
    new THREE.MeshBasicMaterial({vertexColors: THREE.FaceColors}),
];
var current_material = 0;
//var pop_stats;
var encoded_mesh;
var lines;
var meshpath;


function get_new_data () {
    var ctmfile = fs_struct[hemi][surf]["mesh"];
    var statsfile = fs_struct[hemi][surf]["stats"];
    $.ajax({
        url: ajaxcallback,
        method: "POST",
        data: {"ctmfile": ctmfile, "statsfile": statsfile}
    }).done(function(data) {
        encoded_mesh = data.encoded_mesh;
        lines = data.statlines;
        meshpath = ctmfile;
        loadMesh();
    });
}
//function population_statistics () {
    // Load subject population stats
//    $.getJSON(populationpath, function(data) {
//	    pop_stats=data;
//	    console.log(pop_stats);
//   });
//}
function init_gui() {	
	// Connect button functions
	$("#lh").click(selectHemisphere);
	$("#rh").click(selectHemisphere);
	$("#pial").click(selectSurface);
	$("#white").click(selectSurface);		
}
function selectHemisphere() {
    hemi = this.id;
	$("#hemisphere .button").removeClass("selected");
	$(this).addClass("selected");
	get_new_data ();
}
function selectSurface() {
    surf = this.id;
	$("#surface .button").removeClass("selected");
	$(this).addClass("selected");
	get_new_data ();
}
function init_3d() {
	overlay = document.getElementById('overlay');
	container = document.getElementById('container');

	W = $("#container").width();
	H = $("#container").height();

	camera = new THREE.PerspectiveCamera( 50, W / H, 1, 2000 );
	camera.position.z = 200;
	scene = new THREE.Scene();

	// RENDERER
	renderer = new THREE.WebGLRenderer( { antialias: true } );
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.setSize( W, H );
	renderer.domElement.style.position = "relative";
	container.appendChild( renderer.domElement );
	trackball = new THREE.TrackballControls(camera,renderer.domElement);

	// EVENTS
	window.addEventListener('resize', onWindowResize, false);
    var onKeyDown = function(event) {
      if (event.keyCode == 67) { // when 'c' is pressed
        current_material = (current_material + 1) % materials.length
        mesh.material = materials[current_material];
      }
    };
    document.addEventListener("keydown", onKeyDown, false);
}
function loadMesh() {
	var loader = new THREE.CTMLoader();
	$("#overlay").html("Loading...");
	loader.load( meshpath, 
		function( geometry ) {
			mesh = new THREE.Mesh(geometry, materials[current_material]);
            var box = new THREE.Box3().setFromObject(mesh);
            box.center(mesh.position); // this re-sets the mesh position
            mesh.position.multiplyScalar(- 1);
            var pivot = new THREE.Group();
			while(scene.children.length>0)
				scene.remove(scene.children[0]);
            scene.add(pivot);
			scene.add(mesh);
			$("#overlay").html(
                "<b>"+meshoverlay+"</b>"
			);
			loadStats();
		},
		{useWorker: true,callbackProgress:function(obj){
			var pct=parseInt(100*obj.loaded/obj.total);
			if(pct<100)
				$("#overlay").html(pct+"%");
			else
				$("#overlay").html("Decompressing...");
		}}
	);
}
function loadStats() {
	var commn={};
	var tsurf={};
	var thick={};
	var i;

	$("#overlay").append("<br />");
	commn["Total Vertices"]=parseInt(lines[18].split(",")[3]);
	commn["Total Surface Area"]=parseFloat(lines[19].split(",")[3]);
	commn["Mean Cortical Thickness"]=parseFloat(lines[20].split(",")[3]);
	for(i in commn)
		$("#overlay").append(i+": "+commn[i]+"<br/>");

	for(i=53;i<86;i++) {
		tsurf[lines[i].split(/[ ]+/)[0]]=parseFloat(lines[i].split(/[ ]+/)[2]);
		thick[lines[i].split(/[ ]+/)[0]]=parseFloat(lines[i].split(/[ ]+/)[4]);
	}
    $("#overlay").append("<br/><div class='region-name'>Selected Region Name: -select with mouse hover a circle-</div>");
	$("#overlay").append("Regional Surface Area:<br />");
	drawFingerprint({variable:"SurfArea", data:tsurf});
	$("#overlay").append("<br/>Regional Cortical Thickness:<br />");
	drawFingerprint({variable:"ThickAvg", data:thick});
}
function makeSVG(tag, attrs) {
    var el=document.createElementNS("http://www.w3.org/2000/svg",tag);
    for (var k in attrs)
        el.setAttribute(k, attrs[k]);
    return el;
}
function drawFingerprint(param) {
	
	var svg,r,i,d,arr,n,max,val,x,y,path,f;
	
	arr=Object.keys(param.data);
	
	svg=makeSVG('svg',{viewBox:'0,0,110,110',width:200,height:200});
	$("#overlay").append(svg);

	// draw radar circles
	for(r=0;r<=50;r+=12.5)
		$(svg).append(makeSVG('circle',{stroke:(r%25==0)?'#ffffff':'rgba(255,255,255,0.5)','stroke-width':0.5,r:Math.max(r,0.5),cx:55,cy:55,fill:'none'}));

	// draw radar circles units
	var txt=makeSVG('text',{x:50+12.5,y:57,"font-size":8,fill:"#afafaf"});
	txt.innerHTML="-&sigma;&nbsp;&nbsp;&nbsp;&mu;&nbsp;&nbsp;&nbsp;+&sigma;";
    $(svg).append(txt);

	//rect = txt.getBBox(); console.log(rect);
    var rect = {};
    try {
        rect = txt.getBBox();
    } catch(e) {
        // Firefox 3.0.x plays badly here
    } finally {
       rect = rect || {};
    }

	$(svg).append(makeSVG('rect',{x:50+12.5,y:51,width:40,height:8,fill:"rgba(0,0,0,0.5)"}));
	
	// draw fingerprint path
	d=[];
	i=0;
	n=arr.length;
	for(val in param.data) {
		// compute min/max from pop_stats: mean ± s.d.
		min=pop_stats[val][param.variable].m-2*pop_stats[val][param.variable].s;
		max=pop_stats[val][param.variable].m+2*pop_stats[val][param.variable].s;

		// compute subject value
		r=(param.data[val]-min)/(max-min);
		if(r>1) r=1;
		if(r<0) r=0;
		x=55+50*r*Math.cos(2*Math.PI*i/n);
		y=55+50*r*Math.sin(2*Math.PI*i/n);
		d.push( ((i==0)?"M":"L")+x+","+y);
		i++;
	}
	d.push("Z");
	path=makeSVG('path',{id:'path',stroke:'#ffffff','stroke-width':1,fill:'none'});
	path.setAttributeNS(null,'d',d.join(" "));
	$(svg).append(path);

	// draw region dots
	i=0;
	for(val in param.data) {
		// compute min/max from pop_stats: mean ± s.d.
		min=pop_stats[val][param.variable].m-2*pop_stats[val][param.variable].s;
		max=pop_stats[val][param.variable].m+2*pop_stats[val][param.variable].s;

		// compute subject value
		r=(param.data[val]-min)/(max-min);
		f='#ffffff';
		if(r>1){ r=1;f="#ff0000"};
		if(r<0){ r=0;f="#ff0000"};
		x=55+50*r*Math.cos(2*Math.PI*i/n);
		y=55+50*r*Math.sin(2*Math.PI*i/n);
		var reg=makeSVG('circle',{class:'region ',title:val, fill:f, r:2, cx:x, cy:y});
		$(svg).append(reg);
		i++;
	}
	$(".region").css({"pointer-events": "auto"});
	$(".region").hover(function(){
		var x=$(this).attr('cx');
		var y=$(this).attr('cy');
		var svg=$(this).closest("svg")[0];
		var m=svg.getScreenCTM();
		var p=svg.createSVGPoint();
		p.x=x;
		p.y=y;
		var pp=p.matrixTransform(m);
        //document.getElementById("text").style.display = "block";
		//$("#text").css({left:pp.x,top:pp.y});
        $(".region-name").html("Selected Region Name: " + $(this).attr('title'))
		//$("#text").text($(this).attr('title'));
	});
	$(".region").mouseout(function(){
        $(".region-name").html("Selected Region Name: -select with mouse hover a circle-")
	});
}
function onWindowResize( event ) {
	W = $("#container").width();
	H = $("#container").height();
	renderer.setSize( W, H );
	camera.aspect = W/H;
	camera.updateProjectionMatrix();
}	
function animate() {
	requestAnimationFrame( animate );
	render();
}
function render() {
	renderer.render( scene, camera );
	trackball.update();
}
