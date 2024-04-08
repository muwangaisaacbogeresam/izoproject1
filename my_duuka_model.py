from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase
from sqlalchemy import Column, Integer, Text,  Float,String, ForeignKey, create_engine, Boolean, DateTime, Date
from sqlalchemy.sql import func
from datetime import date

engine = create_engine("sqlite:///Dduuka_database.db", echo=True)

class Base(DeclarativeBase):
    pass

class MyProducts(Base):
    __tablename__ = "Products"
    id = Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False, unique=True)
    unit_of_measurement = Column(String, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate= func.now())

    #define relationship
    # Stock = relationship("MyStock", backref="products")
    # sales = relationship("MySales", back_populates='products')

class MyStock(Base):
    __tablename__="Stock"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("Products.id"))
    quantity = Column(Float, default=0.0)
    current_qty = Column(Float, default=0.0)
    amount_bought_at = Column(Float, default=0.0)
    selling_rate = Column(Float, nullable=False)
    product_info = Column(String, default='current qty known')
    stock_active = Column(Boolean, default=True)
    expiry_date = Column(String, default='28-12-05')
    damaged_pdt = Column(Boolean, default=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate= func.now())

    #define these relationships
    # Sales = relationship("MySales", back_populates="stock")
    # products = relationship('MyProducts', back_populates='stock')

class MySales(Base):
    __tablename__ = "Sales"
    id = Column(Integer, primary_key=True)
    product_name = Column(Integer, ForeignKey('Products.id'))
    quantity_sold = Column(Float, default=1.0)
    rate = Column(Float, ForeignKey('Stock.id'))
    amount = Column(Float, default=0.0)
    #pdt_profit = Column(Float, default=0.0)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate= func.now())

    #define these relationships
    # stock = relationship("MyStock", backref='sales') 
    # products = relationship('MyProducts', back_populates='sales')

class Clients(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tele_no = Column(String, unique=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())

class Nycreditors(Base):
    __tablename__="creditors"
    id = Column(Integer, primary_key=True)
    creditor = Column(Integer, ForeignKey('client.id'))
    product_name = Column(Integer, ForeignKey('Products.id'))
    quantity_sold = Column(Float, nullable=False)
    rate = Column(Float, ForeignKey('Stock.id'))
    amount = Column(Float, default=0.0)
    is_cleared = Column(Boolean, default=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate= func.now())
    due_date = Column(String, nullable=True)

class Payments(Base):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("client.id"))
    creditor_sale_id = Column(Integer, ForeignKey('creditors.id'))
    paid_amount = Column(Float, default=0.0)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
class Expenditure(Base):
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True)
    lunch = Column(Float, default=0.0)
    breakfast = Column(Float, default=0.0)
    transport = Column(Float, default=0.0)
    beneficary = Column(String, nullable=False)
    wage = Column(Float, default=0.0)
    salary = Column(Float, default=0.0)
    rent = Column(Float, default=0.0)
    client_discribed_costs = Column(Integer, ForeignKey('client_discribed_cost.id'), nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now()) 

class ClientsDescribedCost(Base):
    __tablename__='client_discribed_cost'
    id = Column(Integer, primary_key=True)
    service_rendered = Column(Text, nullable=False)
    amount = Column(Float, default=0.0)
    beneficary = Column(String, nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now()) 

class AvailiableLiquidity(Base):
    __tablename__ = 'ready_available_cash'
    id = Column(Integer, primary_key=True)
    availiable_cash = Column(Float, default=0.0)
    contributed_capital = Column(Float, default=0.0)
    created_date = Column(Date, default= date.today())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())   

# def createtable():
#     engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     Base.metadata.create_all(engine)
#     session.close()
#     print("database sucessfully created")

# createtable()

# def deletetable():
#     engine = create_engine("sqlite:///Dduuka_database.db", echo=True)
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     Base.metadata.drop_all(engine)

#     session.close()

# deletetable()