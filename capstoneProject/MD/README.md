# Child Stunting Detection App  

A mobile application built using Kotlin to help parents and caregivers detect stunting in children, provide quick tips for prevention, share educational articles, and track their child’s growth history.  

## Features  

### 1. **Stunting Detection**  
- **Input Form:** Allows users to input the child's height, weight, and age.  
- **Machine Learning Model Integration:** Predicts stunting status using pre-trained TensorFlow Lite (TFLite) model.  
- **Result Categories:** Displays results in four categories—`Severely Stunted`, `Stunted`, `Normal`, and `Healthy`.  
- **Dynamic UI Feedback:** Includes a color-coded slider to visually represent the child's growth status.  

### 2. **Quick Tips**  
- **Expert-backed Tips:** Provides actionable tips based on the detected growth status.  
- **Offline Mode:** Saves frequently accessed tips for offline viewing.  
- **Personalized Recommendations:** Adapts suggestions based on user preferences and child’s age.  

### 3. **Related Articles**  
- **Dynamic Content Loading:** Retrieves articles from an API using Retrofit.  
- **Personalized Article:** Showing artilce base on presiction result that user get.  

### 4. **History Tracking**  
- **Data Persistence:** Stores previous detection results using Room Database.  

---

## Technical Overview  

- **Programming Language:** Kotlin  
- **Architecture:** MVVM (Model-View-ViewModel)  
- **Libraries and Tools:**  
  - UI: Material Design Components, RecyclerView  
  - Data Storage: Room Database 
  - Networking: Retrofit, Gson  
  - ML Integration: TensorFlow Lite (TFLite)   
- **Third-party APIs:**  
  - Articles API for fetching parenting-related content.  

---

