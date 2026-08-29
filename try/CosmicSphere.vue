<template>
  <div id="threejs-scene"></div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

interface CustomPointsMaterialParameters extends THREE.PointsMaterialParameters {
  onBeforeCompile?: (shader: THREE.WebGLProgramParametersWithUniforms) => void
}

// 定义类型
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let points: THREE.Points
let clock: THREE.Clock
let animationId: number

const gu = {
  time: { value: 0 }
}

// 初始化场景
const initScene = () => {
  // 创建场景 - 平衡的背景色
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0d0618) // 适中的深紫背景

  // 创建相机
  camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    1,
    1000
  )
  camera.position.set(0, 4, 21)

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true // 支持透明
  })
  renderer.setSize(window.innerWidth, window.innerHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)) // 限制像素比，提升性能

  const container = document.getElementById('threejs-scene')
  if (container) {
    container.appendChild(renderer.domElement)
  }

  // 创建控制器
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.enablePan = false
  controls.minDistance = 10
  controls.maxDistance = 50

  // 创建时钟
  clock = new THREE.Clock()

  // 生成点云
  generatePointCloud()

  // 开始渲染循环
  animate()
}

// 生成点云
const generatePointCloud = () => {
  const pts: THREE.Vector3[] = []
  const sizes: number[] = []
  const shift: number[] = []

  // 创建移动函数
  const pushShift = () => {
    shift.push(
      Math.random() * Math.PI,
      Math.random() * Math.PI * 2,
      (Math.random() * 0.9 + 0.1) * Math.PI * 0.1,
      Math.random() * 0.9 + 0.1
    )
  }

  // 创建中心球体的点（减少到30000个点以提升性能）
  for (let i = 0; i < 30000; i++) {
    sizes.push(Math.random() * 1.2 + 0.3)
    pushShift()
    pts.push(
      new THREE.Vector3()
        .randomDirection()
        .multiplyScalar(Math.random() * 0.5 + 9.5)
    )
  }

  // 创建周围环绕的点（减少到60000个点以提升性能）
  for (let i = 0; i < 60000; i++) {
    const r = 10
    const R = 40
    const rand = Math.pow(Math.random(), 1.5)
    const radius = Math.sqrt(R * R * rand + (1 - rand) * r * r)

    pts.push(
      new THREE.Vector3().setFromCylindricalCoords(
        radius,
        Math.random() * 2 * Math.PI,
        (Math.random() - 0.5) * 2
      )
    )
    sizes.push(Math.random() * 1.2 + 0.3)
    pushShift()
  }

  // 创建点云几何体
  const geometry = new THREE.BufferGeometry().setFromPoints(pts)
  geometry.setAttribute('sizes', new THREE.Float32BufferAttribute(sizes, 1))
  geometry.setAttribute('shift', new THREE.Float32BufferAttribute(shift, 4))

  // 创建点云材质参数
  const materialParams: CustomPointsMaterialParameters = {
    size: 0.125, // 稍微增大粒子
    transparent: true,
    depthTest: false,
    blending: THREE.AdditiveBlending,
    opacity: 0.7, // 提高整体透明度
    onBeforeCompile: (shader: any) => {
      shader.uniforms.time = gu.time
      shader.vertexShader = `
        uniform float time;
        attribute float sizes;
        attribute vec4 shift;
        varying vec3 vColor;
        ${shader.vertexShader}
      `
        .replace(`gl_PointSize = size;`, `gl_PointSize = size * sizes;`)
        .replace(
          `#include <color_vertex>`,
          `#include <color_vertex>
            float d = length(abs(position) / vec3(40., 10., 40.));
            d = clamp(d, 0., 1.);
            // 适中的颜色亮度
            vColor = mix(vec3(180., 65., 145.), vec3(55., 10., 180.), d) / 255.;
          `
        )
        .replace(
          `#include <begin_vertex>`,
          `#include <begin_vertex>
            float t = time;
            float moveT = mod(shift.x + shift.z * t, PI2);
            float moveS = mod(shift.y + shift.z * t, PI2);
            transformed += vec3(cos(moveS) * sin(moveT), cos(moveT), sin(moveS) * sin(moveT)) * shift.w;
          `
        )

      shader.fragmentShader = `
        varying vec3 vColor;
        ${shader.fragmentShader}
      `
        .replace(
          `#include <clipping_planes_fragment>`,
          `#include <clipping_planes_fragment>
            float d = length(gl_PointCoord.xy - 0.5);
          `
        )
        .replace(
          `vec4 diffuseColor = vec4( diffuse, opacity );`,
          // 适中的粒子透明度
          `vec4 diffuseColor = vec4(vColor, smoothstep(0.5, 0.1, length(gl_PointCoord.xy - 0.5)) * 0.5);`
        )
    }
  }

  // 创建点云材质
  const material = new THREE.PointsMaterial(materialParams)

  // 创建点云对象
  points = new THREE.Points(geometry, material)
  points.rotation.order = 'ZYX'
  points.rotation.z = 0.2
  scene.add(points)
}

// 动画循环
const animate = () => {
  animationId = requestAnimationFrame(animate)

  controls.update()

  // 更新时间（稍微减慢旋转速度）
  const t = clock.getElapsedTime() * 0.4
  gu.time.value = t * Math.PI
  points.rotation.y = t * 0.04

  renderer.render(scene, camera)
}

// 处理窗口大小变化
const handleWindowResize = () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
}

// 生命周期钩子
onMounted(() => {
  console.log('🌌 初始化3D星辰宇宙背景...')
  initScene()
  window.addEventListener('resize', handleWindowResize)
})

onBeforeUnmount(() => {
  console.log('🌙 清理3D星辰宇宙背景...')

  // 停止动画循环
  if (animationId) {
    cancelAnimationFrame(animationId)
  }

  // 移除事件监听
  window.removeEventListener('resize', handleWindowResize)

  // 清理Three.js资源
  if (renderer) {
    renderer.setAnimationLoop(null)
  }

  if (scene) {
    scene.traverse((object) => {
      if (object instanceof THREE.Mesh || object instanceof THREE.Points) {
        if (object.geometry) {
          object.geometry.dispose()
        }
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach((material) => material.dispose())
          } else {
            object.material.dispose()
          }
        }
      }
    })
  }

  if (renderer) {
    renderer.dispose()
  }

  // 清理 DOM
  const container = document.getElementById('threejs-scene')
  if (container && renderer.domElement) {
    container.removeChild(renderer.domElement)
  }
})
</script>

<style scoped>
#threejs-scene {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  margin: 0;
  padding: 0;
  pointer-events: none; /* 允许点击穿透 */
}

/* 添加加载动画 - 匹配新的颜色 */
#threejs-scene::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50px;
  height: 50px;
  border: 3px solid rgba(180, 65, 145, 0.25);
  border-top-color: rgba(180, 65, 145, 0.7);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

/* 加载完成后隐藏加载动画 */
#threejs-scene:has(canvas)::before {
  display: none;
}
</style>
