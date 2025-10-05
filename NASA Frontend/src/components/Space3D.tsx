import React, { useEffect, useRef } from "react";
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const Space3D = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    const container = mountRef.current;
    const width = container.clientWidth;
    const height = 600; // Consistent height
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000008, 1.0); // Dark space background
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    container.appendChild(renderer.domElement);

    // Create starfield background
    const starGeometry = new THREE.BufferGeometry();
    const starCount = 2000;
    const starPositions = new Float32Array(starCount * 3);
    
    for (let i = 0; i < starCount * 3; i += 3) {
      starPositions[i] = (Math.random() - 0.5) * 300;     // x - wider spread
      starPositions[i + 1] = (Math.random() - 0.5) * 300; // y
      starPositions[i + 2] = (Math.random() - 0.5) * 300; // z
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
    
    // Enhanced lighting for bigger model
    const ambientLight = new THREE.AmbientLight(0x404040, 0.8);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
    directionalLight.position.set(15, 15, 10);
    scene.add(directionalLight);
    
    const pointLight = new THREE.PointLight(0x4080ff, 0.6);
    pointLight.position.set(-15, -15, -10);
    scene.add(pointLight);

    // Load GLB model
    const loader = new GLTFLoader();
    let earthModel: THREE.Object3D | null = null;
    
    loader.load(
      '/models/earth.glb',
      (gltf) => {
        earthModel = gltf.scene;
        
        // Make the model MUCH bigger
        const box = new THREE.Box3().setFromObject(earthModel);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        const maxSize = Math.max(size.x, size.y, size.z);
        const scale = 20 / maxSize; // Much bigger scale (was 12, now 20)
        earthModel.scale.setScalar(scale);
        
        earthModel.position.sub(center.multiplyScalar(scale));
        
        scene.add(earthModel);
      },
      undefined,
      (error) => {
        console.error('Error loading GLB:', error);
      }
    );
    
    // Camera position with zoom capability
    let cameraDistance = 30; // Starting distance for bigger model
    camera.position.set(0, 8, cameraDistance);
    camera.lookAt(0, 0, 0);
    
    // Animation
    function animate() {
      requestAnimationFrame(animate);
      
      if (earthModel) {
        earthModel.rotation.y += 0.002; // Smooth rotation
        earthModel.rotation.x += 0.0005;
      }
      
      // Slowly rotate starfield
      stars.rotation.y += 0.0001;
      stars.rotation.x += 0.00005;
      
      renderer.render(scene, camera);
    }
    animate();
    
    // Enhanced mouse and zoom controls
    let mouseX = 0;
    let mouseY = 0;
    
    const onMouseMove = (event: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouseY = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      
      // Dynamic camera movement
      const baseX = mouseX * 10;
      const baseY = mouseY * 8 + 8;
      const baseZ = cameraDistance;
      
      camera.position.set(baseX, baseY, baseZ);
      camera.lookAt(0, 0, 0);
    };
    
    // Zoom controls with mouse wheel
    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      cameraDistance += event.deltaY * 0.02;
      cameraDistance = Math.max(10, Math.min(80, cameraDistance)); // Zoom range
      
      const baseX = mouseX * 10;
      const baseY = mouseY * 8 + 8;
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
            Interactive Earth Model
          </h2>
          <p className="text-lg text-white/80 max-w-2xl mx-auto">
            Explore our home planet in stunning 3D detail
          </p>
        </div>
        
        <div 
          ref={mountRef} 
          className="w-full rounded-xl overflow-hidden border border-accent/30 shadow-2xl"
          style={{ height: '600px' }}
        />
        
        <div className="text-center mt-4 text-white/60 text-sm">
          Move mouse to explore • Scroll to zoom in/out • Earth rotates naturally
        </div>
      </div>
    </section>
  );
};

export default Space3D;