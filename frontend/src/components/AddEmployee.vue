<template>
  <div class="add-employee-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-position="top"
      size="large"
    >
      <el-form-item label="Имя сотрудника" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="Введите имя"
          :prefix-icon="User"
        />
      </el-form-item>

      <el-form-item label="Роль" prop="role">
        <el-input
          v-model="formData.role"
          placeholder="Например: бариста, повар, официант..."
          :prefix-icon="Briefcase"
        />
      </el-form-item>

      <el-form-item label="Фото сотрудника">
        <el-upload
          ref="uploadRef"
          class="photo-uploader"
          :auto-upload="false"
          :limit="1"
          accept="image/*"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :file-list="fileList"
          list-type="picture-card"
        >
          <template #default>
            <div class="upload-trigger">
              <el-icon class="avatar-uploader-icon">
                <Plus />
              </el-icon>
              <div class="upload-text">Добавить фото</div>
            </div>
          </template>
          <template #tip>
            <div class="el-upload__tip">
              Желательно крупный портрет лица для лучшего распознавания
            </div>
          </template>
        </el-upload>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="submitting"
          @click="submit"
          style="width: 100%"
          :icon="submitting ? Loading : UserFilled"
        >
          {{ submitting ? 'Сохраняю...' : 'Добавить сотрудника' }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-alert
      v-if="success"
      title="Сотрудник успешно добавлен!"
      type="success"
      :closable="false"
      show-icon
      style="margin-top: 16px"
    >
      <template #default>
        После добавления новых сотрудников перезапустите сервис распознавания для обновления базы.
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { User, Briefcase, Plus, UserFilled, Loading } from '@element-plus/icons-vue';
import { config } from '../config.js';

const backendBase = config.backendUrl;
const emit = defineEmits(['added']);

const formRef = ref();
const uploadRef = ref();
const submitting = ref(false);
const success = ref(false);
const fileList = ref([]);

const formData = reactive({
  name: '',
  role: ''
});

const rules = {
  name: [
    { required: true, message: 'Пожалуйста, введите имя', trigger: 'blur' },
    { min: 2, message: 'Имя должно содержать минимум 2 символа', trigger: 'blur' }
  ]
};

const handleFileChange = (file) => {
  fileList.value = [file];
};

const handleFileRemove = () => {
  fileList.value = [];
};

const submit = async () => {
  if (!formRef.value) return;

  try {
    const valid = await formRef.value.validate();
    if (!valid) return;
  } catch {
    return;
  }

  success.value = false;
  submitting.value = true;

  try {
    const formDataToSend = new FormData();
    formDataToSend.append('name', formData.name);
    formDataToSend.append('role', formData.role);
    
    if (fileList.value.length > 0 && fileList.value[0].raw) {
      formDataToSend.append('photo', fileList.value[0].raw);
    }

    const res = await fetch(backendBase + '/api/employees', {
      method: 'POST',
      body: formDataToSend
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.error || 'Ошибка сервера');
    }

    await res.json();
    
    // Очищаем форму
    formData.name = '';
    formData.role = '';
    fileList.value = [];
    formRef.value.resetFields();
    
    success.value = true;
    emit('added');
    
    ElMessage.success({
      message: 'Сотрудник успешно добавлен!',
      duration: 3000
    });

    // Скрываем сообщение об успехе через 5 секунд
    setTimeout(() => {
      success.value = false;
    }, 5000);
  } catch (e) {
    console.error(e);
    ElMessage.error({
      message: e.message || 'Не удалось добавить сотрудника',
      duration: 4000
    });
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.add-employee-form {
  max-width: 100%;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
}

.photo-uploader {
  width: 100%;
}

:deep(.el-upload-list--picture-card) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0;
}

:deep(.el-upload--picture-card) {
  width: 148px;
  height: 148px;
  border-radius: 12px;
  border: 2px dashed #d9d9d9;
  transition: all 0.3s;
  margin: 0;
}

:deep(.el-upload--picture-card:hover) {
  border-color: #409eff;
}

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 100%;
  color: #8c939d;
}

.avatar-uploader-icon {
  font-size: 28px;
}

.upload-text {
  font-size: 14px;
}

:deep(.el-upload__tip) {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 0.5px;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #5568d3 0%, #63408a 100%);
}
</style>
