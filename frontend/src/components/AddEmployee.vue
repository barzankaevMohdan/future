<template>
  <form @submit.prevent="submit">
    <div class="field">
      <label>Имя *</label>
      <input v-model="name" required />
    </div>
    <div class="field">
      <label>Роль</label>
      <input v-model="role" placeholder="бариста, повар, официант..." />
    </div>
    <div class="field">
      <label>Фото (желательно крупный портрет)</label>
      <input type="file" accept="image/*" @change="onFileChange" />
    </div>
    <button type="submit" :disabled="submitting">
      {{ submitting ? 'Сохраняю...' : 'Добавить сотрудника' }}
    </button>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">Сотрудник добавлен. После добавления новых сотрудников перезапусти сервис распознавания.</p>
  </form>
</template>

<script setup>
import { ref } from 'vue';

const backendBase = 'http://localhost:3000';
const emit = defineEmits(['added']);

const name = ref('');
const role = ref('');
const file = ref(null);
const submitting = ref(false);
const error = ref('');
const success = ref(false);

const onFileChange = (e) => {
  const files = e.target.files;
  if (files && files[0]) {
    file.value = files[0];
  } else {
    file.value = null;
  }
};

const submit = async () => {
  error.value = '';
  success.value = false;
  submitting.value = true;

  try {
    const formData = new FormData();
    formData.append('name', name.value);
    formData.append('role', role.value);
    if (file.value) formData.append('photo', file.value);

    const res = await fetch(backendBase + '/api/employees', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.error || 'Ошибка сервера');
    }

    await res.json();
    name.value = '';
    role.value = '';
    file.value = null;
    success.value = true;
    emit('added');
  } catch (e) {
    console.error(e);
    error.value = e.message || 'Не удалось добавить сотрудника';
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

input {
  padding: 4px 6px;
  font-size: 14px;
}

button {
  padding: 6px 10px;
  font-size: 14px;
  cursor: pointer;
}

.error {
  color: #b00020;
  margin-top: 4px;
}

.success {
  color: #136b2b;
  margin-top: 4px;
  font-size: 13px;
}
</style>
