import React, { useEffect, useRef } from "react";
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const EarthSatelliteView = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    const container = mountRef.current;
    const width = container.clientWidth;
    const height = 600; // Taller for better view
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000008, 1.0); // Darker space background
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    container.appendChild(renderer.domElement);

    // Create starfield background
    const starGeometry = new THREE.BufferGeometry();
    const starCount = 1500;
    const starPositions = new Float32Array(starCount * 3);
    
    for (let i = 0; i < starCount * 3; i += 3) {
      starPositions[i] = (Math.random() - 0.5) * 200;     // x
      starPositions[i + 1] = (Math.random() - 0.5) * 200; // y
      starPositions[i + 2] = (Math.random() - 0.5) * 200; // z
    }
    
    starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    const starMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.3,
      transparent: true,
      opacity: 0.9
    });
    
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
    
    // Lighting - brighter for bigger models
    const ambientLight = new THREE.AmbientLight(0x404040, 0.8);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
    directionalLight.position.set(15, 15, 10);
    scene.add(directionalLight);
    
    const pointLight = new THREE.PointLight(0x4080ff, 0.6);
    pointLight.position.set(-15, -15, -10);
    scene.add(pointLight);

    let earthModel: THREE.Object3D | null = null;
    let satelliteModel: THREE.Object3D | null = null;
    let satelliteOutline: THREE.Object3D | null = null;
    const loader = new GLTFLoader();

    // Load Earth model - MUCH BIGGER
    loader.load('/models/earth.glb', (gltf) => {
      earthModel = gltf.scene;
      
      // Scale Earth much bigger
      const earthBox = new THREE.Box3().setFromObject(earthModel);
      const earthCenter = earthBox.getCenter(new THREE.Vector3());
      const earthSize = earthBox.getSize(new THREE.Vector3());
      const earthMaxSize = Math.max(earthSize.x, earthSize.y, earthSize.z);
      const earthScale = 15 / earthMaxSize; // Much bigger (was 8, now 15)
      
      earthModel.scale.setScalar(earthScale);
      earthModel.position.sub(earthCenter.multiplyScalar(earthScale));
      
      scene.add(earthModel);
    });

    // Load Satellite model - BIGGER and more visible
    loader.load('/models/satellite.glb', (gltf) => {
      satelliteModel = gltf.scene;
      
      // Scale satellite MUCH bigger for maximum visibility
      const satBox = new THREE.Box3().setFromObject(satelliteModel);
      const satCenter = satBox.getCenter(new THREE.Vector3());
      const satSize = satBox.getSize(new THREE.Vector3());
      const satMaxSize = Math.max(satSize.x, satSize.y, satSize.z);
      const satScale = 6 / satMaxSize; // MUCH bigger for visibility (was 3, now 6)
      
      satelliteModel.scale.setScalar(satScale);
      satelliteModel.position.sub(satCenter.multiplyScalar(satScale));
      
      // Add a glowing outline to make satellite more visible
      const satelliteOutline = satelliteModel.clone();
      const outlineMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ffff,
        transparent: true,
        opacity: 0.3,
        side: THREE.BackSide
      });
      
      satelliteOutline.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          child.material = outlineMaterial;
        }
      });
      
      satelliteOutline.scale.multiplyScalar(1.1); // Slightly bigger for outline effect
      scene.add(satelliteOutline);
      scene.add(satelliteModel);
    });
    
    // Camera position - adjusted for better satellite visibility
    let cameraDistance = 28; // Slightly further back to see satellite better
    camera.position.set(5, 8, cameraDistance); // Offset position for better angle
    camera.lookAt(0, 0, 0);
    
    // Animation - SLOWER satellite
    let time = 0;
    function animate() {
      requestAnimationFrame(animate);
      time += 0.003; // Much slower (was 0.01, now 0.003)
      
      // Rotate Earth slower
      if (earthModel) {
        earthModel.rotation.y += 0.001;
      }
      
      // Orbit satellite around Earth - OPTIMIZED for visibility
      if (satelliteModel) {
        const orbitRadius = 22; // Slightly bigger orbit for better view
        
        // Use a tilted orbit for better visibility from multiple angles
        const tiltAngle = Math.PI / 6; // 30 degree tilt
        const x = Math.cos(time) * orbitRadius;
        const z = Math.sin(time) * orbitRadius;
        const y = Math.sin(time * 0.5) * 4 + Math.cos(time) * 2; // More dynamic vertical movement
        
        satelliteModel.position.set(x, y, z);
        
        // Make satellite face Earth
        satelliteModel.lookAt(0, 0, 0);
        
        // Update outline position
        if (satelliteOutline) {
          satelliteOutline.position.copy(satelliteModel.position);
          satelliteOutline.lookAt(0, 0, 0);
        }
      }
      
      // Slowly rotate starfield
      stars.rotation.y += 0.0002;
      
      renderer.render(scene, camera);
    }
    animate();
    
    // Mouse and zoom controls
    let mouseX = 0;
    let mouseY = 0;
    
    const onMouseMove = (event: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouseY = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      
      // Dynamic camera movement with better satellite tracking
      const baseX = mouseX * 8 + 5; // Keep slight offset
      const baseY = mouseY * 6 + 8;
      const baseZ = cameraDistance;
      
      camera.position.set(baseX, baseY, baseZ);
      camera.lookAt(0, 0, 0);
    };
    
    // Zoom controls with mouse wheel
    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      // Zoom with better satellite visibility
      cameraDistance += event.deltaY * 0.01;
      cameraDistance = Math.max(12, Math.min(50, cameraDistance)); // Closer minimum for better satellite view
      
      const baseX = mouseX * 8 + 5;
      const baseY = mouseY * 6 + 8;
      camera.position.set(baseX, baseY, cameraDistance);
      camera.lookAt(0, 0, 0);
    };
    
    container.addEventListener('mousemove', onMouseMove);
    container.addEventListener('wheel', onWheel);
    
    // Handle resize
    const handleResize = () => {
      const newWidth = container.clientWidth;
      camera.aspect = newWidth / height;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, height);
    };
    
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => {
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      container.removeEventListener('mousemove', onMouseMove);
      container.removeEventListener('wheel', onWheel);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, []);

  return (
    <section className="relative py-16 bg-gradient-to-b from-black via-slate-900 to-black">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Earth & Satellite System
          </h2>
          <p className="text-lg text-white/80 max-w-2xl mx-auto">
            Explore our planet and the satellites that help us understand space biology
          </p>
        </div>
        
        <div 
          ref={mountRef} 
          className="w-full rounded-xl overflow-hidden border border-accent/30 shadow-2xl"
          style={{ height: '600px' }}
        />
        
        <div className="text-center mt-4 text-white/60 text-sm">
          Move mouse to explore • Scroll to zoom • Satellite orbits every 2 minutes
        </div>
      </div>
    </section>
  );
};

export default EarthSatelliteView;