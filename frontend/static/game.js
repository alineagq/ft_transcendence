import * as THREE from "three";

// Criar a cena
const scene = new THREE.Scene();

// Carregar imagem de fundo
const loader = new THREE.TextureLoader();
loader.load("/static/background.jpeg", (texture) => {
  scene.background = texture;
});

// Criar a câmera
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);

// Criar o renderizador
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Criar a bola (esfera)
const geometry = new THREE.SphereGeometry(0.79, 32, 32);
const material = new THREE.MeshStandardMaterial({ color: 0xffffff });
const ball = new THREE.Mesh(geometry, material);
ball.position.y = 1;
scene.add(ball);

// Adicionar iluminação
const light = new THREE.PointLight(0xffffff, 15, 100);
light.position.set(1, 1, 1);
scene.add(light);

const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);

// Posicionar a câmera
camera.position.z = 5;

// Loop de animação
function animate() {
  requestAnimationFrame(animate);
  ball.rotation.y += 0.01;
  renderer.render(scene, camera);
}

animate();

// Ajustar ao redimensionamento da janela
window.addEventListener("resize", () => {
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
});
